import Slider from '@material-ui/core/Slider';
import { withStyles } from '@material-ui/core';

const CustomSlider =  withStyles({
    root: {
        color: "#111",
        height: 3,
        padding: "13px 0",
    },
    // track: {
    //     height: 4,
    //     borderRadius: 2,
    // },
    thumb: {
        // height: 20,
        // width: 20,
        // backgroundColor: "#fff",
        // border: "1px solid currentColor",
        // marginTop: -9,
        // marginLeft: -11,
        // boxShadow: "#ebebeb 0 2px 2px",
        // "&:focus, &:hover, &$active": {
            // boxShadow: "#ccc 0 2px 3px 1px",
        // },
        color: "#111",
    },
})(Slider);

export default CustomSlider;