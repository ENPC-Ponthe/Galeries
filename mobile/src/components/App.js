import React, {Component} from 'react';
import {createDrawerNavigator} from 'react-navigation'
import HomeScreen from '../components/HomeScreen'
import firebase from "react-native-firebase";
import type { Notification } from 'react-native-firebase';
import {Text} from "react-native-elements";

function navigationOptions(title) {
    return () => ({
        title: title,
        headerStyle: {
            backgroundColor: '#fec72f',
        },
        headerTintColor: '#fff',
        headerLeft: <Text onPress={() =>
            navigation.navigate('DrawerOpen')}>Menu</Text>
    })
}

const AppStack = createDrawerNavigator({
    Home: {
        screen: HomeScreen,
        navigationOptions: navigationOptions('Galeries Ponthé')
    },
    Page: {
        screen: HomeScreen,
    },
}, {
    headerMode: 'float',
})

export default class App extends Component {
    componentDidMount() {
        firebase.messaging().hasPermission()
            .then(enabled => {
                if (!enabled) {
                    firebase.messaging().requestPermission()
                    return
                }
                this.notificationDisplayedListener = firebase.notifications().onNotificationDisplayed((notification: Notification) => {
                    console.log("Notification displayed")
                })
                this.notificationListener = firebase.notifications().onNotification((notification: Notification) => {
                    console.log("Notification received")
                })
            })
    }

    componentWillUnmount() {
        this.notificationDisplayedListener();
        this.notificationListener();
    }

    render() {
        return <AppStack/>
    }
}
