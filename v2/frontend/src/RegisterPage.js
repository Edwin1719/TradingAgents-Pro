import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Button, Alert } from 'react-bootstrap';
import { FaRobot, FaBitcoin, FaEthereum, FaDollarSign } from 'react-icons/fa';

function RegisterPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setError('');
        try {
            await axios.post('/api/auth/register', { username, password });
            navigate('/login');
        } catch (err) {
            setError('Registration failed. The username might already be taken.');
            console.error('Registration failed', err);
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
                <p>Join the future of automated trading analysis.</p>
            </div>
            <div className="auth-form-panel">
                <div className="auth-card">
                    <h2>Create Account</h2>
                    {error && <Alert variant="danger">{error}</Alert>}
                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label>Username</Form.Label>
                            <Form.Control type="text" placeholder="Choose a unique username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                        </Form.Group>
                        <Form.Group className="mb-4">
                            <Form.Label>Password</Form.Label>
                            <Form.Control type="password" placeholder="Create a strong password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                        </Form.Group>
                        <Button variant="primary" type="submit" className="w-100">
                            Sign Up
                        </Button>
                    </Form>
                    <div className="w-100 text-center mt-4">
                        <small className="text-muted">Already have an account? <Link to="/login">Log In</Link></small>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RegisterPage;
