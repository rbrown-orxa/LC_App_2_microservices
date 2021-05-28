import React from "react";
import { Row, Col } from "react-bootstrap";
import data from "../common/plan.json";

export default function BottomBar() {
    return (
        <div style={{ marginLeft: "-15px", width: "100%" }}>
            <Row>
                <Col lg="9" className="bottom-bar">
                    <Row className="pt-4 pl-4 pb-4">
                        {data.bottomBar.map((item) => {
                            return (
                                <Col md="4" sm="6" xs="12">
                                    <Row>
                                        <Col lg="12">
                                            <img
                                                src={require("../img/dollar_img.png")}
                                                width="39px"
                                                alt=""
                                            />
                                        </Col>
                                        <Col>
                                            <h6 className="bottom-bar-title">
                                                {item.title}
                                            </h6>
                                            <h6 className="bottom-bar-subtitle">
                                                {item.subTitle}
                                            </h6>
                                        </Col>
                                    </Row>
                                </Col>
                            );
                        })}
                    </Row>
                    {/* <small style={{color:'#707070'}}>© 2017-2020 Copyright. OrxaGrid All rights reserved.</small> */}
                </Col>
            </Row>
        </div>
    );
}
