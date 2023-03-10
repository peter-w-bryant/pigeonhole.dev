import React, { useState, useContext } from 'react';
import { Card, Form, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import LoginContext from "../contexts/loginContext";

// import github logo from fontawesome
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import GithubLogin from 'react-github-login';
import axios from 'axios';

import "./Registration.css";

const API_URL = 'http://localhost:5000';  // or your Flask API endpoint URL

function Registration() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState('');

  const [wantToRegister, setWantToRegister] = useState(false);
  const [buttonText, setButtonText] = useState("Login");
  const [switchText, setSwitchText] = useState("Don't have an account? Register here.");

  const [loggedIn, setLoggedIn] = useContext(LoginContext);

  const navigate = useNavigate();

  const handleUsername = (event) => {
    setUsername(event.target.value);
  }

  const handlePassword = (event) => {
    setPassword(event.target.value);
  }

  const handleEmail = (event) => {
    setEmail(event.target.value);
  }

  const handleSwitch = () => {
    wantToRegister ? setWantToRegister(false) : setWantToRegister(true);
    if (wantToRegister) {
      setButtonText("Login");
      setSwitchText("Don't have an account? Register here.")
    } else {
      setButtonText("Register");
      setSwitchText("Already have an account? Login here.");
    }
  }

  const handleLogin = () => {
    fetch('/login', {
      method: 'POST',
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: username,
        password: password
      }),
      credentials: 'include'
    }).then(res => {
      if (res.status === 200) {
        setLoggedIn(username);
      } else if (res.status === 401) {
        alert("username or password wrong");
      } else {
        throw new Error();
      }
    }).catch(err => console.log('login: ' + err));

    navigate('/');
  }

  const handleGitHubOAuth = async () => {
    const callbackUrl = `${window.location.origin}/github_callback`;
  
    // Send the user to the Github authorization page
    window.location.href = `https://github.com/login/oauth/authorize?client_id=${process.env.REACT_APP_GITHUB_CLIENT_ID}&redirect_uri=${callbackUrl}&scope=user:email`;
    // Wait for the user to complete the Github OAuth flow
    window.addEventListener('message', async (event) => {
      if (event.origin !== window.location.origin) {
        return;
      }
      const { data: { code } } = event;

      try {
        // Send the authorization code to the Flask API
        await axios.get(`/github_oauth?code=${code}`);

        console.log('github oauth success');
  
        // Redirect to the main page of your application
        navigate('/');
      } catch (error) {
        console.error(error);  // log the error for debugging
      }
    }, false);
  };
  

  const submit = () => {
    wantToRegister ? handleRegister() : handleLogin();
  }

  const handleRegister = () => {
    fetch('/register', {
      method: 'POST',
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: username,
        password: password,
        email: email
      }),
      credentials: 'include'
    }).then(res => {
      if (res.status === 201) {
        handleLogin();
      } else if (res.status === 409) {
        alert("username already taken");
      } else {
        throw new Error();
      }
    }).catch(err => console.log('register:' + err));
  }

  return (
    <div className='div-registration'>
      <Card className='card-custom'>
        <Card.Header className='card-header-custom'>
          <h5><b>Login</b> or <b>register an account</b> below!</h5>
        </Card.Header>

        <Card.Body>
          <Form>
            <GithubLogin
              clientId={process.env.REACT_APP_GITHUB_CLIENT_ID}
              onSuccess={handleGitHubOAuth}
              onFailure={console.error}
              redirectUri="http://127.0.0.1:3000/"
              scope="user:email"
              buttonText={<span>Login with GitHub <FontAwesomeIcon icon={faGithub} /></span>}
              className='submit'
            />

            <Form.Group className='form-group-custom'>
              <Form.Label>Username</Form.Label>
              <Form.Control placeholder="Enter Username" onChange={handleUsername} />
            </Form.Group>
            <Form.Group className='form-group-custom'>
              <Form.Label>Password</Form.Label>
              <Form.Control type="password" placeholder="Enter Password" onChange={handlePassword} />
            </Form.Group>
            {
              wantToRegister && (
                <Form.Group className='form-group-custom'>
                  <Form.Label>Email</Form.Label>
                  <Form.Control placeholder="Enter Email" onChange={handleEmail} />
                </Form.Group>
              )
            }
            <Button className='submit' variant="primary" type="submit" onClick={submit}>
              {buttonText}
            </Button>
            <Button className='submit' onClick={handleSwitch}>{switchText}</Button>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
}

export default Registration;

