import { StyleSheet } from 'react-native'

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'column',
    backgroundColor: 'black'
  },
  preview: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center'
  },
  imagePreview: {
    flex: 1,
    justifyContent: 'flex-end',
    alignItems: 'center'
  },
  filterParams: {
    flex: 1,
  },
  button: {
    flex: 0,
    backgroundColor: '#fff',
    borderRadius: 5,
    paddingVertical: 10,
    paddingHorizontal: 20,
    alignSelf: 'center',
    margin: 20,
    borderWidth: 1,
    borderColor: '#000'
  },
  disabledButton: {
    flex: 0,
    backgroundColor: '#888',
    borderRadius: 5,
    paddingVertical: 10,
    paddingHorizontal: 20,
    alignSelf: 'center',
    margin: 20
  },
  optionsButton: {
    backgroundColor: '#fff',
    borderRadius: 5,
    paddingVertical: 10,
    paddingHorizontal: 20,
    position: 'absolute',
    top: 15,
    right: 15,
    borderWidth: 1,
    borderColor: '#000'
  },
  saveButton: {
    backgroundColor: '#fff',
    borderRadius: 5,
    paddingVertical: 10,
    paddingHorizontal: 20,
    position: 'absolute',
    top: 15,
    left: 15,
    borderWidth: 1,
    borderColor: '#000'
  },
  spinner: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F5FCFF88'
  },
  filterTitle: {
    flex: 0,
    fontSize: 30,
    marginVertical: 20,
    marginHorizontal: 10,
    color: '#fff'
  },
  ocrTitle: {
    flex: 0,
    fontSize: 30,
    marginVertical: 10,
    textAlign: 'center',
    color: '#000'
  },
  ocrOverlay: {
    flex: 1,
    padding: 10,
    backgroundColor: '#F5FCFF88'
  },
  ocrText: {
    flex: 1,
    fontSize: 25,
    color: '#000'
  },
  ocrNoText: {
    flex: 1,
    fontSize: 25,
    color: '#ff0000'
  },
  backgroundImage: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    right: 0
  },
  capture: {
    width: 70,
    height: 70,
    borderRadius: 35,
    borderWidth: 5,
    borderColor: '#FFF',
    marginBottom: 15,
  },
  cancel: {
    position: 'absolute',
    right: 20,
    top: 20,
    backgroundColor: 'transparent',
    color: '#FFF',
    fontWeight: '600',
    fontSize: 17,
  },
  buttonPannel: {
    flex: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    backgroundColor: '#000'
  }
})

export default styles
