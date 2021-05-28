import React from 'react';
import SpinnerIcon from '../img/Ripple.gif';

export default function Spinner(props) {
    let {isLoading} = props;
    // console.log('Spinner',props,isLoading)s
    return (
        <div class="spinner-2" style={{ display: isLoading ? 'block' : 'none' }}>
            <img src={SpinnerIcon} style={{ width: '12.5vw', }} alt='' />
        </div>);
}