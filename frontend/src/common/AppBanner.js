import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { AZURE_MARKET_PLACE_URL } from "./constants";

const AppBanner = ({ free_calls, max_free_calls }) => {
    return (
        <div id="AppBanner">
            <div class="alert alert-info" role="alert">
                You have <b>{free_calls}</b>/{max_free_calls}{" "}
            remaining results available on your plan, upgrade
            for unlimited results &nbsp;
            <a className="clrBlack" href={AZURE_MARKET_PLACE_URL}>
                    <FontAwesomeIcon icon={faArrowRight} />
                </a>
            </div>
        </div>
    );
};
export default AppBanner;
