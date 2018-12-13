import React, {Component} from 'react';
import {
    View,
    Button,
    ActivityIndicator
} from 'react-native';
import {API_URL} from "../constants";


export default class Galleries extends Component {
    constructor(props) {
        super(props)
        this.state ={
            isLoading: true,
        }
    }

    async componentDidMount() {
        try {
            let response = await fetch(
                API_URL + '/galleries',
            )
            let responseJson = await response.json()
            console.log(responseJson)
            this.setState({
                isLoading: false,
                galleries: responseJson,
            })
        } catch (error) {
            console.error(error)
        }
    }

    render() {
        const { navigate } = this.props.navigation
        const { isLoading, galleries } = this.state
        if (!isLoading) {
            return galleries.map((gallery) =>
                <View>
                    <Button
                        title={gallery.name}
                        onPress={() =>
                            navigate('Gallery', { gallery_slug: gallery.slug })
                        }
                    />
                </View>
            )
        }

        return <ActivityIndicator />
    }
}