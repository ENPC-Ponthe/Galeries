import { StyleSheet } from 'react-native'

export default styles = StyleSheet.create({
    title: {
        fontSize: 30,
        margin: 10,
    },
    textInput: {
        fontSize: 20,
        width: '80%',
        borderColor: 'gray',
        borderWidth: 2,
        borderRadius: 5,
        color: '#fff',
        backgroundColor: '#222',
        padding: 10,
        marginBottom: 10
    },
    logo: {
        marginTop: 10
    },
    submitButton: {
        backgroundColor: '#fec72f',
        borderRadius: 20,
        paddingBottom: 10,
        paddingTop: 10,
        paddingLeft: 20,
        paddingRight: 20,
        marginBottom: 20
    },
    container: {
        flex: 1,
        flexDirection: 'column',
        justifyContent: 'space-between',
        alignItems: 'center'
    }
})

export const IMAGE_SIZE = 250
export const IMAGE_HEIGHT_SMALL = 100
