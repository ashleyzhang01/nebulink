"use client";
import React, { useState } from "react";
import axios from "axios";
import { SearchResults } from "../types";
import { FaSearch, FaQuestionCircle } from 'react-icons/fa';

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

    return (
        <div>
            <div style={{
                width: '600px',
                position: 'relative',
            }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <input
                        type="text"
                        value={searchText}
                        onChange={handleChange}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        placeholder="What are you looking to bring to your network?"
                        style={{
                            flex: 1,
                            padding: '10px',
                            paddingRight: '40px',
                            margin: 0,
                            fontSize: '16px',
                            border: 'none',
                            borderRadius: '20px',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            color: '#333',
                        }}
                    />
                    <FaSearch 
                        style={{ 
                            position: 'absolute', 
                            right: '40px', 
                            color: 'grey',
                            cursor: 'pointer'
                        }} 
                        onClick={handleSearch}
                    />
                    <FaQuestionCircle style={{ marginLeft: '10px', color: '#333', cursor: 'pointer' }} title="Search for organizations or people" />
                </div>
            </div>

            {error && <p style={{ color: "red", marginTop: '10px' }}>{error}</p>}

            {/* Display companies if search_type is "company" */}
            {results && (results.search_type === "company") && (results.linkedin_results?.length > 0) && (
                <div style={{ 
                    maxHeight: '500px', 
                    overflowY: 'auto', 
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    borderRadius: '10px',
                    padding: '15px',
                    marginTop: '10px',
                    width: '500px',
                    color: 'black'
                }}>
                    <h3 style={{ color: 'black' }}>Company Results</h3>
                    {results.linkedin_results.map((company: any, index) => (
                        <div key={index} style={{ 
                            margin: '10px 0', 
                            padding: '10px', 
                            borderRadius: '5px',
                            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                            color: 'black'
                        }}>
                            <h4 style={{ color: 'black' }}>{company.name}</h4>
                            {company.logo && (
                                <img src={company.logo} alt="Logo" style={{ width: '50px', height: '50px', borderRadius: '50%' }} />
                            )}
                            <p style={{ color: 'black' }}><strong>Description:</strong> {company.description}</p>
                            <p style={{ color: 'black' }}><strong>Website:</strong> <a href={company.website} target="_blank" rel="noopener noreferrer" style={{ color: 'black' }}>{company.website}</a></p>
                            <p style={{ color: 'black' }}><strong>Company Size:</strong> {company.company_size}</p>
                            <p style={{ color: 'black' }}><strong>Headquarters:</strong> {company.headquarters}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Display individuals if search_type is "individual" */}
            {results && (results.search_type === "individual") && (
                <div style={{ 
                    maxHeight: '500px', 
                    overflowY: 'auto', 
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    borderRadius: '10px',
                    padding: '15px',
                    marginTop: '10px',
                    width: '500px',
                    color: 'black'
                }}>
                    <h3 style={{ color: 'black' }}>Individual Results</h3>
                    {results.linkedin_results?.length > 0 && (
                        <div>
                            <h4 style={{ color: '#0077B5' }}>LinkedIn Users:</h4>
                            {results.linkedin_results.map((org: any, index) => (
                                <div key={index} style={{ 
                                    margin: '10px 0', 
                                    padding: '10px', 
                                    borderRadius: '5px',
                                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                                    color: 'black'
                                }}>
                                    <h5 style={{ color: 'black' }}>{org.name}</h5>
                                    {org.linkedin_users && org.linkedin_users.map((user: any, userIndex: number) => (
                                        <div key={userIndex} style={{ marginTop: '10px' }}>
                                            <img src={user.profile_picture} alt="Profile" style={{ width: '40px', height: '40px', borderRadius: '50%' }} />
                                            <p style={{ color: 'black' }}><strong>Name:</strong> {user.name}</p>
                                            <p style={{ color: 'black' }}><strong>Header:</strong> {user.header}</p>
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>
                    )}

                    {results.github_results?.length > 0 && (
                        <div>
                            <h4 style={{ color: '#24292e' }}>GitHub Users:</h4>
                            {results.github_results.map((repo: any, index) => (
                                <div key={index} style={{ 
                                    margin: '10px 0', 
                                    padding: '10px', 
                                    borderRadius: '5px',
                                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                                    color: 'black'
                                }}>
                                    <h5 style={{ color: 'black' }}>{repo.path}</h5>
                                    {repo.github_users && repo.github_users.map((user: any, userIndex: number) => (
                                        <div key={userIndex} style={{ marginTop: '10px' }}>
                                            <img src={user.profile_picture} alt="Profile" style={{ width: '40px', height: '40px', borderRadius: '50%' }} />
                                            <p style={{ color: 'black' }}><strong>Username:</strong> {user.username}</p>
                                            <p style={{ color: 'black' }}><strong>Name:</strong> {user.name}</p>
                                            <p style={{ color: 'black' }}><strong>Header:</strong> {user.header}</p>
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
