import React, { useState } from 'react';
import { Lock, User, ArrowLeft } from 'lucide-react';
import './AdminLogin.css';

const AdminLogin = ({ onLoginSuccess, onBackToStore }) => {
    const API_BASE_URL = 'http://localhost:5000/api';
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // Check if this is an admin user
                if (data.customer.email === 'admin@shopscale.com') {
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.customer));
                    onLoginSuccess(data.customer);
                } else {
                    setError('Access denied. Admin credentials required.');
                }
            } else {
                setError(data.error || 'Login failed');
            }
        } catch (error) {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <div className="admin-login-container">
            <div className="admin-login-card">
                <button 
                    onClick={onBackToStore}
                    className="back-button"
                >
                    <ArrowLeft size={20} />
                    Back to Store
                </button>

                <div className="login-header">
                    <div className="login-icon">
                        <Lock size={32} />
                    </div>
                    <h2>Admin Login</h2>
                    <p>Access the admin dashboard</p>
                </div>

                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label className="form-label">
                            <User size={18} />
                            Admin Email
                        </label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            className="form-input"
                            placeholder="admin@shopscale.com"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">
                            <Lock size={18} />
                            Password
                        </label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            className="form-input"
                            placeholder="Enter your password"
                            required
                        />
                    </div>

                    <button 
                        type="submit" 
                        className="login-button"
                        disabled={loading}
                    >
                        {loading ? 'Signing In...' : 'Sign In as Admin'}
                    </button>
                </form>

                <div className="login-info">
                    <h4>Demo Admin Credentials:</h4>
                    <p><strong>Email:</strong> admin@shopscale.com</p>
                    <p><strong>Password:</strong> admin123</p>
                </div>
            </div>
        </div>
    );
};

export default AdminLogin;