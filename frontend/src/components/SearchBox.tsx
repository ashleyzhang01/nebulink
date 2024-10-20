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
                            paddingRight: '40px', // Make room for the search icon
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

            {results && (results.linkedin_results?.length > 0 || results.github_results?.length > 0) && (
                <div style={{ 
                    maxHeight: '500px', 
                    overflowY: 'auto', 
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    borderRadius: '10px',
                    padding: '15px',
                    marginTop: '10px',
                    width: '500px',
                }}>
                    <h3 style={{ color: '#333' }}>Search Results</h3>
                    {/* LinkedIn Organizations */}
                    {results.linkedin_results?.length > 0 && (
                        <div>
                            <h4 style={{ color: '#0077B5' }}>LinkedIn Organizations:</h4>
                            {results.linkedin_results.map((org: any, index) => (
                                <div key={index} style={{ 
                                    margin: '10px 0', 
                                    padding: '10px', 
                                    borderRadius: '5px',
                                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
                                }}>
                                    <h5>{org.name || `Organization ${index + 1}`}</h5>
                                    {org.logo && (
                                        <img src={org.logo} alt="Logo" style={{ width: '50px', height: '50px', borderRadius: '50%' }} />
                                    )}
                                    {Object.entries(org).map(([key, value]: [string, any]) => {
                                        if (key !== 'linkedin_users' && value && typeof value === 'string') {
                                            return <p key={key}><strong>{key}:</strong> {value.length > 50 ? `${value.substring(0, 50)}...` : value}</p>
                                        }
                                        return null;
                                    })}
                                </div>
                            ))}
                        </div>
                    )}
                    {/* GitHub Repositories */}
                    {results.github_results?.length > 0 && (
                        <div>
                            <h4 style={{ color: '#24292e' }}>GitHub Repositories:</h4>
                            {results.github_results.map((repo: any, index) => (
                                <div key={index} style={{ 
                                    margin: '10px 0', 
                                    padding: '10px', 
                                    borderRadius: '5px',
                                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
                                }}>
                                    <h5>{repo.name || `Repository ${index + 1}`}</h5>
                                    {Object.entries(repo).map(([key, value]: [string, any]) => {
                                        if (key !== 'github_users' && value && typeof value === 'string') {
                                            return <p key={key}><strong>{key}:</strong> {value.length > 50 ? `${value.substring(0, 50)}...` : value}</p>
                                        }
                                        return null;
                                    })}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}