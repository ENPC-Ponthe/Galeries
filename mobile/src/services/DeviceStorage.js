import { AsyncStorage } from 'react-native'

export default class DeviceStorage {
    static USER_TOKEN_KEY = 'userToken';

    static async setJWT(value) {
        try {
            await AsyncStorage.setItem(this.USER_TOKEN_KEY, value);
        } catch (error) {
            console.log('AsyncStorage Error in setJWT: ' + error.message);
        }
    }

    static async unsetJWT() {
        try {
            await AsyncStorage.removeItem(this.USER_TOKEN_KEY)
        } catch (error) {
            console.log('AsyncStorage Error in unsetJWT: ' + error.message);
        }
    }

    static async getJWT() {
        try {
            return await AsyncStorage.getItem(this.USER_TOKEN_KEY);
        } catch (error) {
            console.log('AsyncStorage Error in getJWT: ' + error.message);
        }
    }
}
