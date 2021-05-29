
// PROD
// export const GENERIC_API_URL = 'https://lcappapi.azurewebsites.net/';
export const AZURE_MARKET_PLACE_URL = 'https://azuremarketplace.microsoft.com/en-us/marketplace/apps/orxagrid1584097142796.lcappv2?tab=Overview';


// DEV
// export const  GENERIC_API_URL = 'http://localhost:5000/';
let _GENERIC_API_URL = ''
if (window._env_ !== undefined) {
	_GENERIC_API_URL = window._env_.GENERIC_API_URL_FROM_ENV;
}
else {
	_GENERIC_API_URL = 'http://localhost:5000/';
}
export const GENERIC_API_URL = _GENERIC_API_URL


let _COMPANY_LOGO_URL = ''
if (window._env_ !== undefined) {
	_COMPANY_LOGO_URL = window._env_.COMPANY_LOGO_URL;
}
else {
	_COMPANY_LOGO_URL = 'https://www.orxagrid.com/images/logo-03-02-2-250x72.png';
}
export const COMPANY_LOGO_URL = _COMPANY_LOGO_URL


let _COMPANY_WEBSITE_URL = ''
if (window._env_ !== undefined) {
	_COMPANY_WEBSITE_URL = window._env_.COMPANY_WEBSITE_URL;
}
else {
	_COMPANY_WEBSITE_URL = 'https://www.orxagrid.com';
}
export const COMPANY_WEBSITE_URL = _COMPANY_WEBSITE_URL

