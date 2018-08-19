import React, { Component } from 'react'
import { StackNavigator } from 'react-navigation'
import HomeScreen from './upload/HomeScreen'
import CaptureImage from './upload/CaptureImage'
import Recorder from './upload/Recorder'

function navigationOptions(title) {
  return () => ({
    title: title,
    headerStyle: {
        backgroundColor: '#fec72f',
    },
    headerTintColor: '#fff'
  })
}

export default App = StackNavigator({
  Home: { screen: HomeScreen,
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

console.disableYellowBox = true
