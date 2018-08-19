import React, { Component } from 'react'
import {
  View,
  TouchableOpacity,
  ActivityIndicator,
  Alert
} from 'react-native'
import Video from 'react-native-video'
import Icon from 'react-native-vector-icons/FontAwesome'
import IconEntypo from 'react-native-vector-icons/Entypo'
import Octicons from 'react-native-vector-icons/Octicons'
import RNFetchBlob from 'react-native-fetch-blob'
import Camera from 'react-native-camera'
import styles from '../styles.js'
import { API_URL } from '../../constants.js'

const fs = RNFetchBlob.fs

export default class Recorder extends Component {
  constructor(props) {
    super(props)
    this.state = {
      cameraType: 'back',
      mirrorMode: false,
      imagePath: null,
      videoPath: null,
      filter: "Aucun",
      uploading: false,
      recording: false
    }
  }

  takeVideo() {
    this.setState({
      recording: true
    })
    this.camera.capture({
      mode: Camera.constants.CaptureMode.video
    })
    .then((data) => {
       console.log('data', data)
       this.setState({
         videoPath: data.path,
         recording: false
       })
     })
    .catch((err) => {
      console.error('error', err)
      this.setState({
        recording: false
      })
      Alert.alert(
        'Erreur vidéo',
        'L\'enregistrement de la vidéo a échoué.',
        [
          {text: 'OK'}
        ],
        { cancelable: false }
      )
    })
  }

  stopVideo(){
    this.camera.stopCapture()
  }

  changeCameraType() {
    if(this.state.cameraType === 'back') {
      this.setState({
        cameraType : 'front',
        mirrorMode : true
      })
    }
    else {
      this.setState({
        cameraType : 'back',
        mirrorMode : false
      })
    }
  }

  cancelVideo = () => this.setState({ videoPath: null })

  cancelImage = () => this.setState({ imagePath: null })

  _uploadVideo(filter) {
    this.setState({
      uploading: true,
      show_text: false
    })
    const url = API_URL + 'upload'

    RNFetchBlob.fetch('POST', url, {
      'Content-Type' : 'multipart/form-data',
    }, [
      { name : 'image', filename : 'mobile.mp4', type:'video/mp4', data: RNFetchBlob.wrap(this.state.videoPath) },
      // elements without property `filename` will be sent as plain text
      { name : 'filter', data : filter }
    ])
    .then((resp) => {
      let data = JSON.parse(JSON.parse(resp.data))
      this.setState({
        image: data.output_image_url,
        uploading: false,
        text: null
      })
    })
    .catch((error) => {
      console.log('response error: ', error)
      this.setState({ uploading: false })
      Alert.alert(
        'Erreur réseau',
        'Pas de connexion internet ou vidéo trop grosse à traiter en moins d\'une minute.',
        [
          {text: 'OK'}
        ],
        { cancelable: false }
      )
    })
  }

  uploadVideo = function() {
    this._uploadVideo(this.state.filter)
  }

  moveToFile = async function() {
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
    fs.mv(this.state.imagePath, FILENAME).then(() => {
      console.log("Fichier "+FILENAME+" created")
    })
  }

  renderCamera() {
    return (
      <View style={styles.container}>
        <Camera
          ref={ref => {
           this.camera = ref
          }}
          style={styles.preview}
          type={this.state.cameraType}
          captureMode = {Camera.constants.CaptureMode.video}
          //aspect={Camera.constants.Aspect.fill}
          mirrorImage={this.state.mirrorMode}
          keepAwake={true}
          permissionDialogTitle={'Permission to use camera'}
          permissionDialogMessage={'We need your permission to use your camera phone'}
        />
        <View style={styles.buttonPannel}>
          <TouchableOpacity
            onPress={this.takeVideo.bind(this)}
            style={styles.button}
          >
            <IconEntypo name="controller-record" size={30}/>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={this.stopVideo.bind(this)}
            style={styles.button}
          >
            <IconEntypo name="controller-stop" size={30}/>
          </TouchableOpacity>
          { !this.state.recording
            ? <TouchableOpacity
                onPress={this.changeCameraType.bind(this)}
                style={styles.button}
              >
                <Octicons name="mirror" size={30}/>
              </TouchableOpacity>
            : <Octicons name="mirror" size={30} style={styles.disabledButton}/>
          }
        </View>
      </View>
    )
  }

  renderVideo() {
    return (
      <View style={styles.container}>
        <Video
          source={{ uri: this.state.videoPath }}
          style={styles.preview}
          rate={1.0}
          volume={1.0}
          muted={false}
          resizeMode={"cover"}
          onEnd={() => { console.log('Video cancelled !') }}
          repeat={true}
        />
        { this.state.uploading
          &&  <View style={styles.spinner}>
                <ActivityIndicator size="large" color="#000"/>
              </View>
        }
        <View style={styles.buttonPannel}>
          <TouchableOpacity
            onPress={this.cancelVideo.bind(this)}
            style={styles.button}
          >
            <Icon name="remove" size={30}/>
          </TouchableOpacity>
          { !this.state.uploading
            ? <TouchableOpacity
                onPress={this.uploadVideo.bind(this)}
                style={styles.button}
              >
                <Icon name="upload" size={30} />
              </TouchableOpacity>
            : <Icon name="upload" size={30} style={styles.disabledButton}/>
          }
        </View>
      </View>
    )
  }

  renderImage() {
    return (
      <View style={styles.container}>
        <Image
          source={{ uri: this.state.imagePath }}
          style={styles.preview}
        />
        <View style={styles.buttonPannel}>
          <TouchableOpacity
            onPress={this.cancelImage.bind(this)}
            style={styles.button}
          >
            <IconEntypo name="back-in-time" size={30}/>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={this.moveToFile.bind(this)}
            style={styles.saveButton}
          >
            <IconEntypo name="save" size={30} />
          </TouchableOpacity>
        </View>
      </View>
    )
  }

  render() {
    return (
      this.state.imagePath
      ? this.renderImage()
      : this.state.videoPath
        ? this.renderVideo()
        : this.renderCamera()
    )
  }
}
