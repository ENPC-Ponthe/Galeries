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
    buttonPannel: {
        flex: 0,
        flexDirection: 'row',
        justifyContent: 'center',
        backgroundColor: '#000'
    }
})

export default styles
