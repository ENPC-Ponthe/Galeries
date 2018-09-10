import React, { Component } from 'react'
import { View } from 'react-native'
import { Button } from 'react-native-elements'

export default class HomeScreen extends Component {
  render() {
    const { navigate } = this.props.navigation
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'space-around' }}>
        <View></View>
        <Button
          icon={{
            name: 'image',
            size: 40,
            color: 'white'
          }}
          title="PHOTO"
          onPress={() =>
            navigate('Image')
          }
          titleStyle={{ fontWeight: "700", fontSize: 60 }}
          buttonStyle={{
            backgroundColor: "#fec72f",
            width: 200,
            height: 70,
            borderColor: "transparent",
            borderWidth: 0,
            borderRadius: 50
          }}
        />
        <Button
          icon={{
            name: 'camera',
            size: 40,
            color: 'white'
          }}
          title="VIDEO"
          onPress={() =>
            navigate('Video')
          }
          titleStyle={{ fontWeight: "700", fontSize: 60 }}
          buttonStyle={{
            backgroundColor: "#fec72f",
            width: 200,
            height: 70,
            borderColor: "transparent",
            borderWidth: 0,
            borderRadius: 50
          }}
        />
        <Button onPress={this.props.deleteJWT}>
          Log Out
        </Button>
        <View></View>
      </View>
    )
  }
}
