import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Button, Alert } from 'react-bootstrap';
import { FaRobot } from 'react-icons/fa';


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
        <div className="auth-container">
            <div className="auth-card">
                <h2 className="auth-title">
                    <FaRobot />
                    <span>Create Your Account</span>
                </h2>
                {error && <Alert variant="danger">{error}</Alert>}
                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3">
                        <Form.Control type="text" placeholder="Choose a username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                    </Form.Group>
                    <Form.Group className="mb-4">
                        <Form.Control type="password" placeholder="Create a password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                    </Form.Group>
                    <Button variant="primary" type="submit" className="w-100">
                        Register
                    </Button>
                </Form>
                <div className="w-100 text-center mt-3">
                    Already have an account? <Link to="/login" className="auth-link">Login</Link>
                </div>
            </div>
        </div>
    );
}

export default RegisterPage;
