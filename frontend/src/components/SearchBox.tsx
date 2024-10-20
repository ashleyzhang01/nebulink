"use client";
import React, { useState } from "react";
import axios from "axios";
import { SearchResults, LinkedinOrganization, Repository } from "../types";

export default function SearchBox() {
    const [searchText, setSearchText] = useState("");
    const [results, setResults] = useState<SearchResults| null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setSearchText(e.target.value);
        console.log("Search text:", e.target.value);
    }

    const handleSearch = async () => {
        if (!searchText.trim()) {
            setError("Please enter a search term.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // Sending the search query to the backend
            const response = await axios.get("http://localhost:8000/search/perform_search", {
                params: {
                    query: searchText,
                },
            });

            // Storing the search results
            setResults(response.data);
        } catch (err) {
            setError("Something went wrong. Please try again.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="search-container">
            <textarea
                className="search-box"
                value={searchText}
                onChange={handleChange}
                placeholder="Search..."
                style={{ color: "black", backgroundColor: "white", fontSize: "16px" }}
            />
            <button onClick={handleSearch} disabled={loading}>
                {loading ? "Searching..." : "Search"}
            </button>

            {error && <p style={{ color: "red" }}>{error}</p>}

            {results && (
                <div className="results">
                    <h3>Search Results</h3>
                    <div>
                        <h4>LinkedIn Organizations:</h4>
                        {results.linkedin_results?.length ? (
                            results.linkedin_results.map((org: LinkedinOrganization, index) => (
                                <div key={index}>
                                    <h5>Organization {index + 1}</h5>
                                    <ul>
                                        {org.linkedin_users.map((user, userIndex) => (
                                            <li key={userIndex}>
                                                <strong>{user.username}</strong> - {user.role} (From {user.start_date} to {user.end_date})
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))
                        ) : (
                            <p>No LinkedIn organizations found.</p>
                        )}
                    </div>
                    <div>
                        <h4>GitHub Repositories:</h4>
                        {results.github_results?.length ? (
                            results.github_results.map((repo: Repository, index) => (
                                <div key={index}>
                                    <h5>Repository {index + 1}</h5>
                                    <ul>
                                        {repo.github_users.map((user, userIndex) => (
                                            <li key={userIndex}>
                                                <strong>{user.username}</strong> - {user.num_contributions} contributions
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))
                        ) : (
                            <p>No GitHub repositories found.</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
