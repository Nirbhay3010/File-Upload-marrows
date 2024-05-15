import React from 'react'

import {
    Navbar,
    Nav,
    Container
  } from "react-bootstrap";
  
import { useNavigate } from "react-router-dom";


function NavbarComponent() {
const navigate = useNavigate();
  return (
    <Navbar expand="lg" className="bg-body-tertiary">
    <Container>
      <Navbar.Brand >Admin Dashboard</Navbar.Brand>
      <Navbar.Toggle aria-controls="basic-navbar-nav" />
      <Navbar.Collapse id="basic-navbar-nav">
        <Nav className="me-auto">
          <Nav.Link onClick={() => navigate('/upload')}>Upload File</Nav.Link>
          <Nav.Link onClick={() => navigate('/dashboard')}>Movies</Nav.Link>
        </Nav>
      </Navbar.Collapse>
    </Container>
  </Navbar>
  )
}

export default NavbarComponent;