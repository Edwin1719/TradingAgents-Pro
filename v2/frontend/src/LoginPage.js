import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Button, Alert } from 'react-bootstrap';
import { FaRobot } from 'react-icons/fa';


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
        <div className="auth-container">
            <div className="auth-card">
                <h2 className="auth-title">
                    <FaRobot />
                    <span>Trading Agents Pro</span>
                </h2>
                {error && <Alert variant="danger">{error}</Alert>}
                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Control type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-4">
                        <Form.Control type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                    </Form.Group>
                    <Button variant="primary" type="submit" className="w-100">
                        Login
                    </Button>
                </Form>
                <div className="w-100 text-center mt-3">
                    Need an account? <Link to="/register" className="auth-link">Register</Link>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
