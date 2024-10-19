"use client";
import React, { useState } from 'react';

export default function SearchBox() {
    const [searchText, setSearchText] = useState('');

    const handleChange = (e: any) => {
        setSearchText(e.target.value);
    };

    return (
        <div className="search-container">
            <textarea
                className="search-box"
                value={searchText}
                onChange={handleChange}
                placeholder="Search..."
            />
        </div>
    );
}