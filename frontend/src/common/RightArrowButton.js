import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRight } from "@fortawesome/free-solid-svg-icons";

const RightArrowButton = ({ onButtonClick }) => {
    return (
        <button className="btn btn-success" onClick={onButtonClick}>
            <FontAwesomeIcon icon={faArrowRight} />
        </button>
    );
};
export default RightArrowButton;
