"use client";
import React, { useState } from "react";
import axios from "axios";
import { SearchResults } from "../types";
import { FaSearch } from 'react-icons/fa';
import { ImSpinner2 } from 'react-icons/im';

export default function SearchBox() {
    const [searchText, setSearchText] = useState("");
    const [results, setResults] = useState<SearchResults | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchText(e.target.value);
    }

    const handleSearch = async () => {
        if (!searchText.trim()) {
            setError("Please enter a search term.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await axios.get("http://localhost:8000/search/perform_search", {
                params: { query: searchText },
            });
            setResults(response.data);
        } catch (err) {
            setError("Something went wrong. Please try again.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleInputClick = () => {
        setSearchText("");
    };

    return (
        <div>
            <div style={{
                width: '100%',
                maxWidth: '800px',
                position: 'relative',
            }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <input
                        type="text"
                        value={searchText}
                        onChange={handleChange}
                        onClick={handleInputClick}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        placeholder="Discover knowledge, skills, or contacts—what do you need?"
                        style={{
                            flex: 1,
                            padding: '15px',
                            paddingRight: '50px',
                            margin: 0,
                            fontSize: '18px',
                            border: 'none',
                            borderRadius: '20px',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            color: '#fff',
                        }}
                    />
                    {loading ? (
                        <ImSpinner2
                            style={{
                                position: 'absolute',
                                right: '15px',
                                color: 'grey',
                                animation: 'spin 1s linear infinite',
                                cursor: 'not-allowed'
                            }}
                        />
                    ) : (
                        <FaSearch
                            style={{
                                position: 'absolute',
                                right: '15px',
                                color: 'grey',
                                cursor: 'pointer'
                            }}
                            onClick={handleSearch}
                        />
                    )}
                </div>
            </div>

            {error && <p style={{ color: "red", marginTop: '10px' }}>{error}</p>}

            {/* Display companies if search_type is "company" */}
            {results && (results.search_type === "company") && (results.linkedin_results?.length > 0) && (
                <div style={{
                    maxHeight: '500px',
                    overflowY: 'auto',
                    backgroundColor: 'rgba(60, 60, 60, 0.9)',
                    borderRadius: '10px',
                    padding: '15px',
                    marginTop: '10px',
                    width: '100%',
                    maxWidth: '800px',
                    color: 'white'
                }}>
                    <h3 style={{ color: 'white' }}>Company Results</h3>
                    {results.linkedin_results.map((company: any, index) => (
                        <div key={index} style={{
                            margin: '10px 0',
                            padding: '10px',
                            borderRadius: '5px',
                            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                            color: 'white'
                        }}>
                            <h4 style={{ color: 'white' }}>{company.name}</h4>
                            {company.logo && (
                                <img src={company.logo} alt="Logo" style={{ width: '50px', height: '50px', borderRadius: '50%' }} />
                            )}
                            <p style={{ color: 'white' }}><strong>Description:</strong> {company.description}</p>
                            <p style={{ color: 'white' }}><strong>Website:</strong> <a href={company.website} target="_blank" rel="noopener noreferrer" style={{ color: 'white' }}>{company.website}</a></p>
                            <p style={{ color: 'white' }}><strong>Company Size:</strong> {company.company_size}</p>
                            <p style={{ color: 'white' }}><strong>Headquarters:</strong> {company.headquarters}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Display individuals if search_type is "individual" */}
            {results && (results.search_type === "individual") && (
                <div style={{
                    maxHeight: '500px',
                    overflowY: 'auto',
                    backgroundColor: 'rgba(60, 60, 60, 0.9)',
                    borderRadius: '10px',
                    padding: '15px',
                    marginTop: '10px',
                    width: '100%',
                    maxWidth: '800px',
                    color: 'white'
                }}>
                    {results.linkedin_user_results?.length > 0 && (
                        <div>
                            {results.linkedin_user_results.map((user: any, index) => (
                                <div key={index} style={{
                                    margin: '10px 0',
                                    padding: '10px',
                                    borderRadius: '5px',
                                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                                    color: 'white'
                                }}>
                                    <h5 style={{ color: 'white' }}>{user.name}</h5>
                                    <p style={{ color: 'white' }}><strong>Header:</strong> {user.header}</p>
                                    <img src={user.profile_picture} alt="Profile" style={{ width: '40px', height: '40px', borderRadius: '50%' }} />
                                </div>
                            ))}
                        </div>
                    )}

                    {results.github_results?.length > 0 && (
                        <div>
                            {results.github_results.map((repo: any, index) => (
                                <div key={index} style={{
                                    margin: '10px 0',
                                    padding: '10px',
                                    borderRadius: '5px',
                                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                                    color: 'white'
                                }}>
                                    <h5 style={{ color: 'white' }}>{repo.path}</h5>
                                    {repo.github_users && repo.github_users.map((user: any, userIndex: number) => (
                                        <div key={userIndex} style={{ marginTop: '10px' }}>
                                            <img src={user.profile_picture} alt="Profile" style={{ width: '40px', height: '40px', borderRadius: '50%' }} />
                                            <p style={{ color: 'white' }}><strong>Username:</strong> {user.username}</p>
                                            <p style={{ color: 'white' }}><strong>Name:</strong> {user.name}</p>
                                            <p style={{ color: 'white' }}><strong>Header:</strong> {user.header}</p>
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
