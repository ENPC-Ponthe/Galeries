import React from 'react'
import {createDrawerNavigator} from 'react-navigation'
import HomeScreen from '../components/HomeScreen'

function navigationOptions(title) {
    return () => ({
        title: title,
        headerStyle: {
            backgroundColor: '#fec72f',
        },
        headerTintColor: '#fff'
    })
}

export default AppStack = createDrawerNavigator({
    Home: {
        screen: HomeScreen,
        navigationOptions: navigationOptions('Galeries Ponthé')
    },
    Page: {
        screen: HomeScreen,
        navigationOptions: navigationOptions('Page')
    },
})
