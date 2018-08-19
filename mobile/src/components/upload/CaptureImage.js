import React, { Component } from 'react'
import {
  Text,
  TouchableOpacity,
  View,
  Image,
  ScrollView,
  ActivityIndicator,
  Clipboard,
  Alert
} from 'react-native'
import { RNCamera } from 'react-native-camera'
import RNFetchBlob from 'react-native-fetch-blob'
import { CheckBox } from 'react-native-elements'
import Icon from 'react-native-vector-icons/FontAwesome'
import IconEntypo from 'react-native-vector-icons/Entypo'
import IconIonicons from 'react-native-vector-icons/Ionicons'
import ImagePicker from 'react-native-image-picker'
import styles from '../styles.js'
import { API_URL, imageFilters } from '../../constants.js'

const fs = RNFetchBlob.fs

var options = {
  storageOptions: {
    skipBackup: true,
    path: 'GaleriesPonthe'
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

class FilterScreen extends Component {
  constructor(props) {
    super(props)
    this.state = {
      initial_image: this.props.image,
      image: this.props.image,
      uploading: false,
      show_filter_panel: false,
      filter: "Aucun"
    }
  }

  back() {
    this.setState({
      image: this.state.initial_image,
      text: null,
      show_text: false
    })
  }

  cancel() {
    this.props.backToCaptureScreen()
  }

  _uploadPhoto(filter) {
    this.setState({
      uploading: true,
      show_text: false
    })
    const url = API_URL + "upload"

    RNFetchBlob.fetch('POST', url, {
      'Content-Type' : 'multipart/form-data',
    }, [
      { name : 'image', filename : 'mobile.jpg', type:'image/jpeg', data: this.state.image },
      // elements without property `filename` will be sent as plain text
      { name : 'filter', data : filter }
    ])
    .then((resp) => {
      let data = JSON.parse(JSON.parse(resp.data))
      RNFetchBlob.fetch('GET', data.output_image_url)
      .then((res) => {
        this.setState({
          image: res.base64(),
          uploading: false,
          text: null
        })
        this.setState({
          text: data.text,
          show_text: true
        })
      })
      .catch((errorMessage, statusCode) => {
        console.log("Error downloading the filtered image")
        Alert.alert(
          'Erreur réseau',
          'Vérifiez que vous êtes bien connecté à internet.',
          [
            {text: 'OK'}
          ],
          { cancelable: false }
        )
      })
    })
    .catch((error) => {
      console.log('response error: ', error)
      this.setState({ uploading: false })
      Alert.alert(
        'Erreur réseau',
        'Pas de connexion internet ou image trop grosse à traiter en moins d\'une minute.',
        [
          {text: 'OK'}
        ],
        { cancelable: false }
      )
    })
  }

  uploadPhoto = function() {
    this._uploadPhoto(this.state.filter)
  }

  chooseFilter() {
    this.setState({ show_filter_panel: !this.state.show_filter_panel })
  }

  copy() {
    Clipboard.setString(this.state.text)
  }

  saveToFile = async function() {
    let FOLDER = fs.dirs.PictureDir+'/GaleriesPonthe'
    await RNFetchBlob.fs.isDir(FOLDER)
    .then((isDir) => {
      if (!isDir) {
        RNFetchBlob.fs.mkdir(FOLDER)
        console.log('Répertoire '+FOLDER+' created')
      }
    })
    let now = new Date()
    let SS = now.getSeconds()
    let MM = now.getMinutes()
    let HH = now.getHours()
    let dd = now.getDate()
    let mm = now.getMonth()+1
    let yyyy = now.getFullYear()
    let TIMESTAMP = [yyyy, mm, dd, HH, MM, SS].join('_')
    let FILENAME = FOLDER+'/'+TIMESTAMP+'.jpg'
    fs.createFile(FILENAME, this.state.image, 'base64')
    .then(() => {
      console.log("Fichier "+FILENAME+" created")
    })
  }

  render() {
    return (
      <View style={styles.container}>
        { this.state.show_filter_panel
          ? <View style={styles.container}>
              <Text style={styles.filterTitle}> Filtre </Text>
              <ScrollView>
                { imageFilters.map((filter, id) => (
                    <CheckBox
                      key={id}
                      title={filter}
                      checkedIcon='dot-circle-o'
                      uncheckedIcon='circle-o'
                      checked={ this.state.filter === filter }
                      onPress={() => { this.setState({ filter: filter}) }}
                    />
                  ))
                }
              </ScrollView>
            </View>
          : <View style={styles.container}>
              <View style={styles.container}>
                <Image source={{ uri: 'data:image/jpeg;base64,'+this.state.image }} style={styles.backgroundImage}/>
              </View>
              { this.state.uploading
                &&  <View style={styles.spinner}>
                      <ActivityIndicator size="large" color="#000"/>
                    </View>
              }
              <View style={styles.buttonPannel}>
                { this.state.image !== this.state.initial_image
                  ? (!this.state.uploading
                    ? <TouchableOpacity
                        onPress={this.back.bind(this)}
                        style={styles.button}
                      >
                        <IconEntypo name="back-in-time" size={30} />
                      </TouchableOpacity>
                    : <IconEntypo name="back-in-time" size={30} style={styles.disabledButton}/>
                  )
                  : <TouchableOpacity
                      onPress={this.cancel.bind(this)}
                      style={styles.button}
                    >
                      <Icon name="remove" size={30} />
                    </TouchableOpacity>
                }
                { !this.state.uploading
                  ? <TouchableOpacity
                      onPress={this.uploadPhoto.bind(this)}
                      style={styles.button}
                    >
                      <Icon name="upload" size={30} />
                    </TouchableOpacity>
                  : <Icon name="upload" size={30} style={styles.disabledButton}/>
                }
              </View>
              <TouchableOpacity
                onPress={this.saveToFile.bind(this)}
                style={styles.saveButton}
              >
                <IconEntypo name="save" size={30} />
              </TouchableOpacity>
            </View>
        }
        <TouchableOpacity
          onPress={this.chooseFilter.bind(this)}
          style={styles.optionsButton}
        >
          <IconIonicons name="md-options" size={30} />
        </TouchableOpacity>
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

  backToCaptureScreen = () => { this.updateImage(null) }

  updateImage(uri) {
    this.setState({
      image: uri
    })
  }

  render() {
    return (
      <View style={styles.container}>
        { this.state.image === null
          ? <PreviewScreen updateImage={this.updateImage.bind(this)}/>
          : <FilterScreen backToCaptureScreen={this.backToCaptureScreen.bind(this)} image={this.state.image}/>
        }
      </View>
    )
  }
}
