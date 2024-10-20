// src/types.ts

export interface LinkedinUserContribution {
    username: string;
    role: string;
    start_date: string;
    end_date: string;
}

export interface LinkedinOrganization {
    linkedin_users: LinkedinUserContribution[];
}

export interface GithubUserContribution {
    username: string;
    num_contributions: number;
}

export interface Repository {
    github_users: GithubUserContribution[];
}

export interface SearchResults {
    search_type: string;
    linkedin_results: LinkedinOrganization[];
    github_results: Repository[];
}
