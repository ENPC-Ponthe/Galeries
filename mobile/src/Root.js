import React from 'react'
import {createSwitchNavigator} from 'react-navigation'
import App from './components/App'
import AuthLoadingScreen from "./screens/AuthLoadingScreen";
import LoginScreen from "./screens/LoginScreen";

export default Root = createSwitchNavigator(
    {
        AuthLoading: AuthLoadingScreen,
        App: App,
        Login: LoginScreen,
    },
    {
        headerMode: 'none',
        initialRouteName: 'AuthLoading',
    }
)

console.disableYellowBox = true
