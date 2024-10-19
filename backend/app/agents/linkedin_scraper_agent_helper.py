import re
from typing import Optional, Set, Tuple
from app.utils.linkedin_scraper import LinkedInScraper
from app.schemas import LinkedinUser as LinkedinUserSchema, LinkedinOrganization as LinkedinOrganizationSchema
from app.db.linkedin_user_functions import get_linkedin_user_by_username, update_linkedin_user, create_linkedin_user
from app.db.linkedin_organization_functions import add_user_to_organization, get_linkedin_organization_by_id, create_linkedin_organization, update_linkedin_organization
from sqlalchemy.orm import Session
from datetime import datetime

def get_linkedin_user_2_degree_network(email: str, password: str, db: Session):
    linkedin_scraper = LinkedInScraper(email, password)
    linkedin_scraper.login()
    processed_users: Set[str] = set()
    processed_organizations: Set[str] = set()

    def process_user_network(username, depth=0):
        if depth > 2 or username in processed_users:
            return

        try:
            db_linkedin_user = get_linkedin_user_by_username(username, db)

            user_profile_url = f"https://www.linkedin.com/in/{username}/"
            print(f"user_profile_url: {user_profile_url}")
            if not user_profile_url:
                print(f"Could not find profile URL for user: {username}")
                return

            if not db_linkedin_user:
                username = user_profile_url.split('/in/')[-1].strip('/')
                db_linkedin_user = create_linkedin_user(LinkedinUserSchema(username=username), db)

            experience_links, education_links = linkedin_scraper.scrape_user_companies(user_profile_url)
            print(f"experience_links: {experience_links}")
            print(f"education_links: {education_links}")
            for company_info in experience_links + education_links:
                if company_info['url'] in processed_organizations:
                    continue

                try:
                    processed_organizations.add(company_info['url'])
                    company_details = linkedin_scraper.scrape_company_info(company_info['url'])
                    
                    if not company_details:
                        continue
                        
                    company_linkedin_id = re.search(r'/company/([\w-]+)/', company_info['url']).group(1)
                    db_organization = get_linkedin_organization_by_id(company_linkedin_id, db)
                    org_schema = LinkedinOrganizationSchema(**company_details, linkedin_id=company_linkedin_id)

                    if not db_organization:
                        db_organization = create_linkedin_organization(org_schema, db)
                    else:
                        db_organization = update_linkedin_organization(org_schema, db)
                    print(f"created or updated organization: {db_organization.name}")
                    date_range = company_info.get('date_range')
                    start_date, end_date = parse_date_range(date_range)

                    add_user_to_organization(
                        db_organization.linkedin_id,
                        db_linkedin_user.username,
                        company_info['role_or_degree'],
                        start_date,
                        end_date,
                        db
                    )
                    processed_users.add(username)
                    print(f"added user {username} to organization: {db_organization.name}")
                    company_people = linkedin_scraper.scrape_company_people(company_info['url'])

                    for person in company_people:
                        person_username = list(person.keys())[0]
                        person_info = person[person_username]

                        if person_username in processed_users:
                            continue

                        try:
                            # contact_info = linkedin_scraper.scrape_person_contact_info(person_username)
                            person_schema = LinkedinUserSchema(
                                username=person_username,
                                name=person_info['name'],
                                header=person_info['header'],
                                profile_picture=person_info['profile_picture'],
                                # email=contact_info.get('email'),
                                # external_websites=contact_info.get('external_websites', [])
                                email=None,
                                external_websites=None
                            )

                            db_person = get_linkedin_user_by_username(person_username, db)
                            if not db_person:
                                db_person = create_linkedin_user(person_schema, db)
                            else:
                                update_linkedin_user(person_schema, db)

                            add_user_to_organization(
                                db_organization.linkedin_id,
                                db_person.username,
                                None,  # We don't have role information for company people
                                None,  # We don't have start date for company people
                                None,  # We don't have end date for company people
                                db
                            )

                            print(f"added user {person_username} to organization: {db_organization.name}")

                            if depth < 1:
                                process_user_network(person_username, depth + 1)
                        except Exception as e:
                            print(f"Error processing user network: {e}")
                            continue
                except Exception as e:
                    print(f"Error processing user network: {e}")
                    continue
        except Exception as e:
            print(f"Error processing user network: {e}")
        
    user_profile_url = linkedin_scraper.get_user_profile_url()
    if user_profile_url:
        initial_username = user_profile_url.split('/in/')[-1].strip('/')
        process_user_network(initial_username)
    else:
        print("Could not find user profile URL")

    linkedin_scraper.logout()


def parse_date_range(date_range: Optional[str]) -> Tuple[Optional[datetime], Optional[datetime]]:
    if not date_range:
        return None, None

    date_range = date_range.strip()
    
    # Case 1: Only one date (assumed to be start date)
    if ' - ' not in date_range:
        try:
            start_date = datetime.strptime(date_range, '%b %Y')
            return start_date, None
        except ValueError:
            return None, None

    # Case 2: Start and end date
    start_str, end_str = date_range.split(' - ')
    
    try:
        start_date = datetime.strptime(start_str, '%b %Y')
    except ValueError:
        start_date = None

    if end_str.lower() == 'present':
        end_date = None
    else:
        try:
            end_date = datetime.strptime(end_str, '%b %Y')
        except ValueError:
            end_date = None

    return start_date, end_date
