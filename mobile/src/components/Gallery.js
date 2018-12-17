import ImageBrowser, {ImageSource} from 'react-native-interactive-image-gallery'
import React, {PureComponent} from 'react';
import {ActivityIndicator, View} from 'react-native';
import {url, get} from "../services/HttpClient";

export default class Gallery extends PureComponent<Props> {
    constructor(props) {
        super(props)
        this.state ={
            isLoading: true,
            gallery_slug: this.props.navigation.getParam('gallery_slug')
        }
        console.log(this.state.gallery_slug)
    }

    onFetch = (data) => {
        this.setState({
            isLoading: false,
            data,
        })
    }

    async componentDidMount(){
        get('/galleries/' + this.state.gallery_slug, this.onFetch)
    }


    render() {
        if(this.state.isLoading){
            return(
                <View style={{flex: 1, padding: 20}}>
                    <ActivityIndicator/>
                </View>
            )
        }

        const imageURLs: Array<ImageSource> = this.state.data.files.map(
            (img: Object, index: number) => ({
                URI: url(img.uri),
                thumbnail: url(img.thumbnail),
                id: String(index),
                title: img.name,
                description: img.description
            })
        )

        const { navigate } = this.props.navigation
        return <ImageBrowser images={imageURLs} closeText="Retour" />
    }
}