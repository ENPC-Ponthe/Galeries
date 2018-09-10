import React from 'react'
import {createDrawerNavigator} from 'react-navigation'
import HomeScreen from '../components/upload/HomeScreen'
import CaptureImage from '../components/upload/CaptureImage'
import Recorder from '../components/upload/Recorder'

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
    Image: {
        screen: CaptureImage,
        navigationOptions: navigationOptions('Partage de Photo')
    },
    Video: { screen: Recorder,
        navigationOptions: navigationOptions('Partage de vidéo')
    },
})
