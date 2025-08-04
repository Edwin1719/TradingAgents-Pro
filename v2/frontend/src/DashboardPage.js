import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Navbar, Form, Button, Card, Spinner, Alert, Row, Col, ListGroup, Badge
} from 'react-bootstrap';
import { FaRobot, FaChartLine, FaSignOutAlt } from 'react-icons/fa';
import axios from 'axios';

// Create an Axios instance for API requests
const apiClient = axios.create({
  baseURL: '/api',
});

// Add a request interceptor to include the token in headers
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

function DashboardPage() {
  const [form, setForm] = useState({
    ticker: 'BTC-USD',
    date: new Date().toISOString().split('T')[0],
    deep_think_llm: '',
    quick_think_llm: '',
  });
  const [tasks, setTasks] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await apiClient.post('/analyze', form);
      const { task_id } = response.data;
      setTasks(prev => ({
        ...prev,
        [task_id]: { id: task_id, status: 'PENDING', result: null, ticker: form.ticker }
      }));
    } catch (err) {
      setError('Failed to submit task. Is the backend running?');
      console.error(err);
    }
    setLoading(false);
  };

  const checkTaskStatus = useCallback(async (taskId) => {
    try {
      const response = await apiClient.get(`/tasks/${taskId}`);
      const { status, result } = response.data;
      if (status === 'SUCCESS' || status === 'FAILURE') {
        setTasks(prev => ({
          ...prev,
          [taskId]: { ...prev[taskId], status, result }
        }));
      } else {
         setTasks(prev => ({
          ...prev,
          [taskId]: { ...prev[taskId], status }
        }));
      }
    } catch (err) {
      console.error(`Failed to check status for task ${taskId}`, err);
    }
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      Object.keys(tasks).forEach(taskId => {
        if (tasks[taskId].status !== 'SUCCESS' && tasks[taskId].status !== 'FAILURE') {
          checkTaskStatus(taskId);
        }
      });
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [tasks, checkTaskStatus]);

  const renderResult = (result) => {
    if (!result) return null;
    const decision = result.final_trade_decision || {};
    return (
      <ListGroup>
        <ListGroup.Item>
          <strong>Final Decision:</strong>{' '}
          <Badge bg={decision.action === 'STRONG_BUY' ? 'success' : 'danger'}>
            {decision.action}
          </Badge>
        </ListGroup.Item>
        <ListGroup.Item>
          <strong>Confidence:</strong> {decision.confidence}
        </ListGroup.Item>
        <ListGroup.Item>
          <strong>Reasoning:</strong> {result.investment_plan}
        </ListGroup.Item>
      </ListGroup>
    );
  };

  return (
    <>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand href="#home">
            <FaRobot className="me-2" /> Trading Agents Pro
          </Navbar.Brand>
          <Navbar.Toggle />
          <Navbar.Collapse className="justify-content-end">
            <Button variant="outline-light" onClick={handleLogout}>
              <FaSignOutAlt className="me-2" /> Logout
            </Button>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container className="mt-4">
        <Row>
          <Col md={4}>
            <Card>
              <Card.Header>
                <FaChartLine className="me-2" />
                New Analysis Task
              </Card.Header>
              <Card.Body>
                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Label>Ticker</Form.Label>
                    <Form.Control
                      type="text"
                      name="ticker"
                      value={form.ticker}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Date</Form.Label>
                    <Form.Control
                      type="date"
                      name="date"
                      value={form.date}
                      onChange={handleInputChange}
                      required
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Deep Think LLM (Optional)</Form.Label>
                    <Form.Control
                      type="text"
                      name="deep_think_llm"
                      placeholder="Default: gpt-4o"
                      value={form.deep_think_llm}
                      onChange={handleInputChange}
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Quick Think LLM (Optional)</Form.Label>
                    <Form.Control
                      type="text"
                      name="quick_think_llm"
                      placeholder="Default: gpt-4o"
                      value={form.quick_think_llm}
                      onChange={handleInputChange}
                    />
                  </Form.Group>
                  <Button variant="primary" type="submit" disabled={loading}>
                    {loading ? <Spinner as="span" animation="border" size="sm" /> : 'Run Analysis'}
                  </Button>
                </Form>
                {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
              </Card.Body>
            </Card>
          </Col>
          <Col md={8}>
            <h2>Analysis Tasks</h2>
            {Object.values(tasks).length === 0 ? (
              <p>No tasks submitted yet.</p>
            ) : (
              Object.values(tasks).map(task => (
                <Card key={task.id} className="mb-3">
                  <Card.Header>
                    Task ID: {task.id} | Ticker: {task.ticker}
                  </Card.Header>
                  <Card.Body>
                    <Card.Title>Status: {task.status}</Card.Title>
                    {task.status === 'PENDING' || task.status === 'STARTED' || task.status === 'PROCESSING' ? (
                      <Spinner animation="border" />
                    ) : task.status === 'SUCCESS' ? (
                      renderResult(task.result)
                    ) : (
                      <Alert variant="danger">
                        Task Failed: {task.result ? JSON.stringify(task.result) : 'Unknown error'}
                      </Alert>
                    )}
                  </Card.Body>
                </Card>
              ))
            )}
          </Col>
        </Row>
      </Container>
    </>
  );
}

export default DashboardPage;