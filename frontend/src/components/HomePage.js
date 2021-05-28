import React, { PureComponent } from "react";
import BottomBar from "./BottomBar";
import StartPage from "./StartPage";

export default class HomePage extends PureComponent {
    componentWillMount() {
        setTimeout(() => {
            let AppHeader = document.getElementsByClassName("App-header")[0];
            AppHeader.style.background = "none";
        }, 500);
        // if (this.props.accountInfo !== undefined) {
        //   return <Redirect to='/SolarPVForm' />
        // }
    }

    render() {
        return (
            <>
                <div class="container">
                    <div class="col">
                        <StartPage nextStep={this.nextStep} />
                    </div>
                    <div class="col"></div>
                </div>
                <BottomBar />
            </>
        );
    }
}
