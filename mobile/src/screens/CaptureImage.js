import React, { Component } from 'react'
import {
  TouchableOpacity,
  View,
} from 'react-native'
import { RNCamera } from 'react-native-camera'
import Icon from 'react-native-vector-icons/FontAwesome'
import IconEntypo from 'react-native-vector-icons/Entypo'
import ImagePicker from 'react-native-image-picker'
import styles from './capture-styles.js'

var options = {
  storageOptions: {
    skipBackup: true,
    path: 'Ponthe'
  }
}

class PreviewScreen extends Component {
  constructor(props) {
    super(props)
  }

  takePhoto = async function() {
    let options = {
      quality: 0.5,
      base64: true
    }
    if (this.camera) {
      const data = await this.camera.takePictureAsync(options)
      this.props.updateImage(data.base64)
    }
  }

  launchCamera() {
    ImagePicker.launchCamera(options, (response) => {
      if (response.didCancel) {
        console.log('User cancelled launchCamera')
      }
      else if (response.error) {
        console.log('launchCamera Error: ', response.error)
      }
      else {
        console.log('Photo taken at '+response.path)
        this.props.updateImage(response.data)
      }
    })
  }

  launchLibrary() {
    ImagePicker.launchImageLibrary(options, (response) => {
      if (response.didCancel) {
        console.log('User cancelled launchLibrary')
      }
      else if (response.error) {
        console.log('launchLibrary Error: ', response.error)
      }
      else {
        console.log('Photo taken at '+response.path)
        this.props.updateImage(response.data)
      }
    })
  }

  render() {
    return (
      <View style={styles.container}>
        <RNCamera
          ref={ref => {
            this.camera = ref
          }}
          style={styles.preview}
          type={RNCamera.Constants.Type.back}
          //flashMode={RNCamera.Constants.FlashMode.on}
          permissionDialogTitle={'Permission to use camera'}
          permissionDialogMessage={'We need your permission to use your camera phone'}
        />
        <View style={styles.buttonPannel}>
          <TouchableOpacity
            onPress={this.takePhoto.bind(this)}
            style={styles.button}
          >
            <Icon name="camera" size={30}/>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={this.launchCamera.bind(this)}
            style={styles.button}
          >
            <Icon name="mobile-phone" size={30}/>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={this.launchLibrary.bind(this)}
            style={styles.button}
          >
            <IconEntypo name="folder-images" size={30}/>
          </TouchableOpacity>
        </View>
      </View>
    )
  }
}


export default class CaptureImage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      image: null
    }
  }

  static navigationOptions = {
    title: 'Capture d\'image'
  }

  backToCaptureScreen = () => { this.updateImage(null) }

  updateImage(uri) {
    this.setState({
      image: uri
    })
  }

  render() {
    return (
      <View style={styles.container}>
          <PreviewScreen updateImage={this.updateImage.bind(this)}/>
      </View>
    )
  }
}
