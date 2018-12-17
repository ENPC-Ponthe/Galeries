import React, {Component} from 'react';
import {
    ActivityIndicator,
    StatusBar,
    View,
} from 'react-native';
import styles from './styles'
import DeviceStorage from '../services/DeviceStorage'

export default class AuthLoadingScreen extends Component {
    constructor(props) {
        super(props);
        this.bootstrapAuth();
    }

    bootstrapAuth () {
        DeviceStorage.getJWT().then((userToken) => {
            console.log("bootstrapping")
            console.log(userToken)
            this.props.navigation.navigate(userToken ? 'App' : 'Login');
        });
    };

    render() {
        return (
            <View style={styles.container}>
                <ActivityIndicator />
                <StatusBar barStyle="default" />
            </View>
        );
    }
}