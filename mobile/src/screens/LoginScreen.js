import React, {Component} from 'react'
import {
    View,
    TextInput,
    Text,
    Animated,
    Keyboard
} from 'react-native'
import logo from '../assets/logo.png'
import {Button} from "react-native-elements"
import styles, { IMAGE_SIZE, IMAGE_HEIGHT_SMALL} from './styles'
import deviceStorage from '../services/deviceStorage'
import {API_URL} from '../constants'
import axios from 'axios'

export default class LoginScreen extends Component {
    constructor(props) {
        super(props);
        this.state = {
            email: '',
            password: '',
            displaySubmitButton: true
        };

        this.keyboardHeight = new Animated.Value(0);
        this.imageSize = new Animated.Value(IMAGE_SIZE);

        this.loginUser = this.loginUser.bind(this)
    }

    componentWillMount () {
        this.keyboardDidShowSub = Keyboard.addListener('keyboardDidShow', this.keyboardDidShow);
        this.keyboardDidHideSub = Keyboard.addListener('keyboardDidHide', this.keyboardDidHide);
    }

    componentWillUnmount() {
        this.keyboardDidShowSub.remove();
        this.keyboardDidHideSub.remove();
    }

    keyboardDidShow = (event) => {
        Animated.parallel([
            Animated.timing(this.keyboardHeight, {
                duration: event.duration,
                toValue: event.endCoordinates.height,
            }),
            Animated.timing(this.imageSize, {
                duration: event.duration,
                toValue: IMAGE_HEIGHT_SMALL,
            }),
        ]).start();
        this.setState({displaySubmitButton: false})
    };

    keyboardDidHide = (event) => {
        const duration = event ? event.duration : 500;
        Animated.parallel([
            Animated.timing(this.keyboardHeight, {
                duration: duration,
                toValue: 0,
            }),
            Animated.timing(this.imageSize, {
                duration: duration,
                toValue: IMAGE_SIZE,
            }),
        ]).start();
        this.setState({displaySubmitButton: true})
    };

    async loadJWT(token) {
        await deviceStorage.setJWT(token);
        console.log(token);
        this.props.navigation.navigate('App')
    }

    loginUser() {
        console.log("Let's login !");
        axios.post(API_URL + "/login",{
            email: this.state.email,
            password: this.state.password
        }).then((response) => {
            this.loadJWT(response.data.token)
        }).catch((error) => {
            console.log(error)
        })
    }
    render() {
        return (
            <Animated.View style={[styles.container, { paddingBottom: this.keyboardHeight }]}>
                <Animated.Image source={logo} style={[styles.logo, { height: this.imageSize, width: this.imageSize }]} />
                <View style={{
                    width: '100%',
                    alignItems: 'center'
                }}>
                    <Text style={styles.title}>Email</Text>
                    <TextInput
                        style={styles.textInput}
                        placeholder={'prenom.nom@eleves.enpc.fr'}
                        placeholderTextColor={'#bbb'}
                        onChangeText={(email) => this.setState({email})}
                        value={this.state.email}
                    />
                    <Text style={styles.title}>Mot de passe</Text>
                    <TextInput
                        style={styles.textInput}
                        placeholder={'password'}
                        placeholderTextColor={'#bbb'}
                        onChangeText={(password) => this.setState({password})}
                        value={this.state.password}
                        secureTextEntry={true}
                    />
                </View>
                { this.state.displaySubmitButton
                    ?   <Button
                            buttonStyle={styles.submitButton}
                            textStyle={{fontSize: 25}}
                            onPress={this.loginUser}
                            title="Se connecter"
                        />
                    :   null
                }
            </Animated.View>
        )
    }
}
