import ImageBrowser, {ImageSource} from 'react-native-interactive-image-gallery'
import React, {PureComponent} from 'react';
import {ActivityIndicator, View} from 'react-native';
import {API_URL, BASE_URL} from "../constants";

export default class Gallery extends PureComponent<Props> {
    loadGallery = async () => {
        try {
            let response = await fetch(
                API_URL + '/galleries/chats',
            )
            let responseJson = await response.json()
            console.log(responseJson)
            this.setState({
                isLoading: false,
                gallery: responseJson,
            })
        } catch (error) {
            console.error(error)
        }
    }

    constructor(props) {
        super(props)
        this.state ={ isLoading: true }
    }

    componentDidMount(){
        this.loadGallery()
    }


    render() {
        if(this.state.isLoading){
            return(
                <View style={{flex: 1, padding: 20}}>
                    <ActivityIndicator/>
                </View>
            )
        }

        const imageURLs: Array<ImageSource> = this.state.gallery.files.map(
            (img: ImageSource, index: number) => ({
                URI: BASE_URL + img.uri,
                thumbnail: BASE_URL + img.thumbnail,
                id: String(index),
                title: img.name,
                description: img.description
            })
        )

        return <ImageBrowser images={imageURLs} />
    }
}