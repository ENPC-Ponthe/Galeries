import ImageBrowser, {ImageSource} from 'react-native-interactive-image-gallery'
import React, {PureComponent} from 'react';

export default class Gallery extends PureComponent<Props> {
    render() {
        const images: Array<ImageSource> = [{
            uri: 'https://ponthe.enpc.org/uploads/ndlr/ofDiA4d4uzxSytQBLEx6.JPG',
            id: 1,
            thumbnail: 'https://ponthe.enpc.org/thumbs/ndlr/ofDiA4d4uzxSytQBLEx6_226x226_fit_90.JPG',
            title: "wesh",
            description: "Des barres la NDLR",
        }, {
            uri: 'https://ponthe.enpc.org/uploads/ndlr/X2vi1PYT7l2br1VZvtJa.JPG',
            id: 1,
            thumbnail: 'https://ponthe.enpc.org/thumbs/ndlr/X2vi1PYT7l2br1VZvtJa_226x226_fit_90.JPG',
            title: "hey",
            description: "Trop kali",
        }]
        const imageURLs: Array<ImageSource> = images.map(
            (img: ImageSource, index: number) => ({
                URI: img.uri,
                thumbnail: img.thumbnail,
                id: String(index),
                title: img.title,
                description: img.description
            })
        )
        return <ImageBrowser images={imageURLs} />
    }
}