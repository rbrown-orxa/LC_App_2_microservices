import React, { PureComponent } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { AZURE_MARKET_PLACE_URL } from "../common/constants";

export default class StartSitePage extends PureComponent {
    getPlanName(plan_id) {
        switch (plan_id) {
            case "m1":
                return "Basic plan";
            case "m2":
                return "Silver plan";
            case "m3":
                return "Gold plan";
            default:
                return "Free plan";
        }
    }

    renderMessage(plan_id, free_calls, max_free_calls) {
        if(plan_id === undefined) {
            return (<div></div>)
        }
        if (plan_id === null) {
            return (
                <div>
                    {plan_id}You have <b>{free_calls}</b>/{max_free_calls} remaining
                    results available on your {this.getPlanName(plan_id)},<br />{" "}
                    upgrade for unlimited results and sharing ability
                </div>
            );
        } else
        return (
            <div>
                {plan_id}You are subscribed to {this.getPlanName(plan_id)},<br /> upgrade
                for unlimited results and sharing ability
            </div>
        );
    }
    render() {
        let {
            resolveApiError,
            resolveApiResponseStatus,
            free_calls,
            max_free_calls,
            plan_id,
        } = this.props;

        let disabledNextButton =
            resolveApiResponseStatus !== 200 ||
            free_calls === null ||
            free_calls === 0;

        return (
            <div class='col-lg-12'>
                {resolveApiError !== undefined && resolveApiError.length > 0 && (
                    <div id="AppBanner">
                        <div class="alert alert-danger" role="alert">
                            {resolveApiError}
                        </div>
                    </div>
                )}

                <div class="row">
                    <div class="caption col-lg-5">
                        <div class="col-md-12">
                            <br />
                            <br />
                            <span>Welcome Back, {this.props.firstName}</span>
                            <p>We hope you are having a wonderful day!</p>
                        </div>
                    </div>
                    <div
                        class="contents"
                        style={{
                            borderRadius:
                                window.innerWidth > 500 ? "25px" : "0px",
                            marginLeft: window.innerWidth > 500 ? "10%" : "0%",
                        }}
                    >
                        <div class="col-md-12">
                            <div className="col control-label-heading">
                                <button
                                    onClick={this.props.nextStep}
                                    // disabled={disabledNextButton}
                                    className="arrow-round-btn"
                                >
                                    <FontAwesomeIcon
                                        icon={faArrowRight}
                                        color={"#fff"}
                                    />
                                </button>
                                &nbsp; START A NEW SITE
                            </div>
                            <div className="col mt-3">
                                {this.renderMessage(
                                    plan_id,
                                    free_calls,
                                    max_free_calls
                                )}
                            </div>
                            <br />
                            <br />
                            <br />
                            <div className="text-center">
                                <a
                                    class="btn btn-success"
                                    href={AZURE_MARKET_PLACE_URL}
                                >
                                    Upgrade
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
