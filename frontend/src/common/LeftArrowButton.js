import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft } from "@fortawesome/free-solid-svg-icons";

const LeftArrowButton = ({ onButtonClick }) => {
    return (
        <button className="btn btn-light" onClick={onButtonClick}>
            <FontAwesomeIcon icon={faArrowLeft} color="#000" />
        </button>
    );
};
export default LeftArrowButton;
