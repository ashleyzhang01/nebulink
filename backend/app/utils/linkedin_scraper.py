import re
from time import sleep
from typing import List, Dict, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

SITE: str = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'


class LinkedInScraper:
    def __init__(self, username: str | None = None, password: str | None = None):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()

    def login(self):
        self.driver.get(SITE)
        username_field = self.driver.find_element(By.NAME, 'session_key')
        if self.username:
            username_field.send_keys(self.username)
        password_field = self.driver.find_element(By.NAME, 'session_password')
        if self.password:
            password_field.send_keys(self.password)
            log_in_button = self.driver.find_element(By.XPATH, '//*[@type="submit"]')
            log_in_button.click()
            sleep(8)
        else:
            sleep(15)  # allow user to login manually

    def get_user_profile_url(self) -> Optional[str]:
        self.driver.get("https://www.linkedin.com/feed/")
        sleep(2)

        try:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                        "div.scaffold-layout__sidebar .artdeco-card.pb4.mb2.overflow-hidden a[href*='/in/']")
                    )).get_attribute('href')
        except Exception as e:
            print(f"Could not find the user profile link: {e}")
            return None

    def scrape_user_companies(self, user_profile_url: str) -> Tuple[List[dict], List[dict]]:
        experience_links = self._scrape_company_links(f"{user_profile_url}details/experience/")
        education_links = self._scrape_company_links(f"{user_profile_url}details/education/")
        return experience_links, education_links

    def scrape_company_people(self, url: str) -> List[Dict]:
        self.driver.get(url if 'people' in url else f"{url}people/")
        sleep(3)

        people: list = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)

            people.extend([
                {person_info['linkedin_id']: {
                    'name': person_info['name'],
                    'header': person_info['header'],
                    'profile_picture': person_info['profile_picture']
                }}
                for card in self.driver.find_elements(By.CSS_SELECTOR, "li.org-people-profile-card__profile-card-spacing")
                if (person_info := self._extract_person_info(card))
                and not any(person_info['linkedin_id'] in person for person in people)
            ])

            if (new_height := self.driver.execute_script("return document.body.scrollHeight")) == last_height:
                break
            last_height = new_height

        self.driver.execute_script("window.scrollTo(0, 0);")
        sleep(2)

        return people

    def scrape_person_contact_info(self, linkedin_id: str) -> Dict:
        contact_info_url = f"https://www.linkedin.com/in/{linkedin_id}/overlay/contact-info/"
        self.driver.get(contact_info_url)
        sleep(2)

        contact_info: dict = {
            'email': None,
            'github': None,
            'external_websites': []
        }

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.artdeco-modal__content"))
            )
            modal_content = self.driver.find_element(By.CSS_SELECTOR, "div.artdeco-modal__content").get_attribute('outerHTML')
            soup = BeautifulSoup(modal_content, 'html.parser')

            if email_element := soup.select_one('a[href^="mailto:"]'):
                contact_info['email'] = email_element.get('href').replace('mailto:', '')

            website_elements = soup.select('section h3:contains("Websites") + ul a') or soup.select('section h3:contains("Website") + ul a')

            github_link = None
            external_links = []
            for element in website_elements:
                href = element.get('href')
                if "github.com" in href:
                    github_link = href
                else:
                    external_links.append(href)

            contact_info['github'] = github_link
            contact_info['external_websites'] = external_links

        except Exception as e:
            print(f"Error scraping contact info for {linkedin_id}: {e}")

        return contact_info

    def scrape_company_info(self, company_url: str) -> Dict:
        self.driver.get(f"{company_url}about/")
        sleep(1.5)

        company_info = {}
        try:
            if name_element := self.driver.find_element(By.CSS_SELECTOR, "h1.org-top-card-summary__title"):
                company_info['name'] = name_element.text.strip()

            if logo_element := self.driver.find_element(By.CSS_SELECTOR, "div.org-top-card-primary-content__logo-container img"):
                company_info['logo_url'] = logo_element.get_attribute('src')

            overview_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section.org-about-module__margin-bottom"))
            )
            html_content = overview_section.get_attribute('outerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')

            if overview_p := soup.find('p', class_='break-words'):
                company_info['description'] = overview_p.text.strip()

            if dl_element := soup.find('dl', class_='overflow-hidden'):
                for dt_element in dl_element.find_all('dt'):
                    current_heading = dt_element.find('h3').text.strip().lower()
                    dd_element = dt_element.find_next_sibling('dd')

                    if current_heading == 'website':
                        company_info[current_heading] = dd_element.find('a')['href']
                    elif current_heading == 'company size':
                        size_text = dd_element.contents[0].strip() if dd_element.contents else ''
                        company_info['company_size'] = size_text
                    elif current_heading in ['industry', 'headquarters', 'specialties']:
                        company_info[current_heading] = dd_element.text.strip()

            return company_info

        except Exception as e:
            print(f"Error scraping company info: {e}")
            return {}

    def scrape_company_filters(self, company_url: str) -> Dict:
        self.driver.get(f"{company_url}people/")
        sleep(3)

        filters: dict = {}
        completed_filter_types: set = set()
        next_clicks_needed: int = 0

        try:
            try:
                show_more_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.org-people__show-more-button"))
                )
                self.driver.execute_script("arguments[0].click();", show_more_button)
                sleep(.5)
            except TimeoutException:
                print("'Show more' button not found or not clickable")

            while True:
                if not self._click_next(next_clicks_needed):
                    print("Failed to navigate back to the correct carousel page")
                    break

                self._process_company_filters_page(filters, completed_filter_types, next_clicks_needed)

                completed_filter_types.update(filters.keys())

                if not (next_button := self.driver.find_element(By.CSS_SELECTOR, "button.artdeco-pagination__button--next")):
                    break
                if next_button.get_attribute("class") and "artdeco-button--disabled" in next_button.get_attribute("class"):
                    break
                next_clicks_needed += 1
                sleep(.5)

        except Exception as e:
            print(f"An error occurred: {e}")
        return filters

    def logout(self):
        try:
            self.driver.get("https://www.linkedin.com/m/logout/")
            sleep(2)
            print("Successfully logged out of LinkedIn")
        except Exception as e:
            print(f"Error during logout: {e}")

    def _scrape_company_links(self, page_url: str) -> List[Dict]:
        self.driver.get(page_url)
        sleep(3)
        company_info_list = []

        main_element = self.driver.find_element(By.CSS_SELECTOR, "main.scaffold-layout__main")
        sections = main_element.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")

        for section in sections:
            company_info = {}

            try:
                company_link = section.find_element(By.CSS_SELECTOR, "a.optional-action-target-wrapper")
                company_info['url'] = company_link.get_attribute('href')

                if role_or_degree_element := section.find_element(By.CSS_SELECTOR, "span.t-14.t-normal"):
                    company_info['role_or_degree'] = role_or_degree_element.text.strip()
                else:
                    company_info['role_or_degree'] = ''

                if not any(edu_term in company_info['role_or_degree'].lower() for edu_term in ['bachelor', 'master', 'phd', 'certificate', 'diploma']):
                    try:
                        role_element = section.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
                        company_info['role'] = role_element.text.strip()
                    except NoSuchElementException:
                        company_info['role'] = None

                try:
                    date_range_element = section.find_element(By.CSS_SELECTOR, "span.t-14.t-normal.t-black--light")
                    company_info['date_range'] = date_range_element.text.strip()
                except NoSuchElementException:
                    company_info['date_range'] = None

                company_info_list.append(company_info)

            except NoSuchElementException:
                print("No such element exception")
                continue

        return company_info_list

    def _extract_person_info(self, card) -> Optional[Dict]:
        try:
            profile_link = card.find_element(By.CSS_SELECTOR, "a.app-aware-link").get_attribute('href')
            return {
                'linkedin_id': profile_link.split('/')[-1].split('?')[0],
                'name': card.find_element(By.CSS_SELECTOR, "div.org-people-profile-card__profile-title").text.strip(),
                'header': card.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__subtitle").text.strip(),
                'profile_picture': card.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__image img").get_attribute('src')
            }
        except Exception as e:
            print(f"Error processing a profile card: {e}")
            return None

    def _click_element_with_retry(self, selector: str, by: str = By.CSS_SELECTOR, max_attempts: int = 3) -> bool:
        for _ in range(max_attempts):
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((by, selector))
                )
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except (StaleElementReferenceException, NoSuchElementException) as e:
                sleep(1)
                print(f"Failed to click element after {max_attempts} attempts: {e}")
        return False

    def _click_next(self, clicks_needed: int) -> bool:
        return all(self._click_element_with_retry("button.artdeco-pagination__button--next") for _ in range(clicks_needed))

    def _process_company_filters_page(self, filters: Dict, completed_filter_types: set, next_clicks_needed: int) -> None:
        try:
            insights_container = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "org-people__insights-container"))
            )
            html_content = insights_container.get_attribute('outerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')

            filter_sections = soup.find_all('div', class_=lambda x: x and x.startswith('artdeco-card p4 m2'))

            for section in filter_sections:
                filter_elements = section.find_all('button', class_='org-people-bar-graph-element')
                for element in filter_elements:
                    if (count := int(element.find('strong').text)) < 3:
                        continue
                    name = element.find('span', class_='org-people-bar-graph-element__category').text.strip()

                    element_xpath = f"//button[contains(@class, 'org-people-bar-graph-element') and .//span[contains(@class, 'org-people-bar-graph-element__category') and text()='{name}']]"

                    if self._click_element_with_retry(element_xpath, by=By.XPATH):
                        sleep(.5)

                        if filter_param := re.search(r'(facet\w+)=([\w\d]+)', self.driver.current_url):
                            filter_type, filter_id = filter_param.groups()
                            if filter_type not in completed_filter_types:
                                filters.setdefault(filter_type, {})[filter_id] = {"name": name, "num_people": count}

                        self.driver.execute_script("window.history.go(-1)")
                        sleep(.5)

                        if not self._click_next(next_clicks_needed):
                            print("Failed to navigate back to the correct carousel page")
                            return

        except Exception as e:
            print(f"Error processing current page: {e}")
