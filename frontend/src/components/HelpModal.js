import React,{useState} from 'react';
import Modal from 'react-bootstrap/Modal'
import {Button} from 'react-bootstrap';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {faInfoCircle} from "@fortawesome/free-solid-svg-icons";
export default function HelpModal(props) {
    const [show, setShow] = useState(false);
  
    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);
  
    return (
      <>
        <FontAwesomeIcon
                onClick={handleShow}
                icon={faInfoCircle}
                size="1x"
                color="#B0B0B0"
        />
        <Modal show={show} onHide={handleClose} style={{position:'fixed',top:'50%',left:'auto'}}>
          {/* <Modal.Header closeButton>
            <Modal.Title>Modal heading</Modal.Title>
          </Modal.Header> */}
          <Modal.Body>{props.info}</Modal.Body>
          {/* <buttondal.Footer>
            <Button variant="secondary" onClick={handleClose}>
              Close
            </Button>
            <Button variant="primary" onClick={handleClose}>
              Save Changes
            </Button>
          </Modal.Footer> */}
        </Modal>
      </>
    );
  }