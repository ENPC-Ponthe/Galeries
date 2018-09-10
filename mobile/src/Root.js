import React from 'react'
import {createSwitchNavigator} from 'react-navigation'
import AppStack from './components/AppStack'
import AuthLoadingScreen from "./screens/AuthLoadingScreen";
import LoginScreen from "./screens/LoginScreen";

export default Root = createSwitchNavigator(
    {
        AuthLoading: AuthLoadingScreen,
        App: AppStack,
        Login: LoginScreen,
    },
    {
        initialRouteName: 'AuthLoading',
    }
);

console.disableYellowBox = true
