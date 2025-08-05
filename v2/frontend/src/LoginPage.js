import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Button, Alert } from 'react-bootstrap';
import { FaRobot, FaBitcoin, FaEthereum, FaDollarSign } from 'react-icons/fa';

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setError('');
        try {
            const response = await axios.post('/api/auth/token', new URLSearchParams({
                username: username,
                password: password
            }));
            localStorage.setItem('token', response.data.access_token);
            navigate('/dashboard');
        } catch (err) {
            setError('Login failed. Please check your username and password.');
            console.error('Login failed', err);
        }
    };

    return (
        <div className="auth-wrapper">
            <div className="auth-brand-panel">
                <div className="floating-icons">
                    <FaBitcoin className="floating-icon i-1" />
                    <FaEthereum className="floating-icon i-2" />
                    <FaDollarSign className="floating-icon i-3" />
                    <FaBitcoin className="floating-icon i-4" />
                    <FaEthereum className="floating-icon i-5" />
                    <FaDollarSign className="floating-icon i-6" />
                </div>
                <FaRobot size={60} />
                <h1>Trading Agents Pro</h1>
                <p>Your AI-powered partner in financial markets.</p>
            </div>
            <div className="auth-form-panel">
                <div className="auth-card">
                    <h2>Welcome Back</h2>
                    {error && <Alert variant="danger">{error}</Alert>}
                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label>Username</Form.Label>
                            <Form.Control type="text" placeholder="Enter your username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                        </Form.Group>
                        <Form.Group className="mb-4">
                            <Form.Label>Password</Form.Label>
                            <Form.Control type="password" placeholder="Enter your password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                        </Form.Group>
                        <Button variant="primary" type="submit" className="w-100">
                            Login
                        </Button>
                    </Form>
                    <div className="w-100 text-center mt-4">
                        <small className="text-muted">Don't have an account? <Link to="/register">Sign Up</Link></small>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
