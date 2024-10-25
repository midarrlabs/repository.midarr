"""
Compatible with Kodi 20.x "Nexus"
"""
import os
import sys

import xbmcgui
import xbmcplugin
from xbmcaddon import Addon
import json
import urllib.request
from urllib.parse import urlencode, parse_qsl

# Get the plugin url in plugin:// notation.
URL = sys.argv[0]
# Get a plugin handle as an integer number.
HANDLE = int(sys.argv[1])

SETTINGS = Addon().getSettings()


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{}?{}'.format(URL, urlencode(kwargs))


def get_videos(mediatype, page):
    request = urllib.request.Request(
        f"{SETTINGS.getString('baseurl')}/api/{mediatype}?token={SETTINGS.getString('apitoken')}&page={page}", headers={
            "Content-Type": "application/json"
        })

    with urllib.request.urlopen(request) as response:
        data = response.read()
        response_data = json.loads(data.decode("utf-8"))
        videos = response_data.get("items", [])

        return videos


def get_item(itemid):
    request = urllib.request.Request(
        f"{SETTINGS.getString('baseurl')}/api/series/{itemid}?token={SETTINGS.getString('apitoken')}", headers={
            "Content-Type": "application/json"
        })

    with urllib.request.urlopen(request) as response:
        data = response.read()
        response_data = json.loads(data.decode("utf-8"))

        return response_data


def get_episodes(itemid, season):
    request = urllib.request.Request(
        f"{SETTINGS.getString('baseurl')}/api/series/{itemid}?season={season}&token={SETTINGS.getString('apitoken')}",
        headers={
            "Content-Type": "application/json"
        })

    with urllib.request.urlopen(request) as response:
        data = response.read()
        response_data = json.loads(data.decode("utf-8"))

        return response_data


def list_seasons(itemid):
    xbmcplugin.setContent(HANDLE, 'files')

    # Get the list of videos in the category.
    videos = get_item(itemid)
    # Iterate through videos.
    for video in range(videos['seasonCount']):
        # Create a list item with a text label
        list_item = xbmcgui.ListItem(label=f"season-{(video + 1)}")

        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use only poster for simplicity's sake.
        # In a real-life plugin you may need to set multiple image types.

        # Set additional info for the list item via InfoTag.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        info_tag = list_item.getVideoInfoTag()
        info_tag.setTitle(f"Season {(video + 1)}")

        xbmcplugin.addDirectoryItem(handle=HANDLE,
                                    url=get_url(action='list-episodes', itemid=videos['id'], season=(video + 1)),
                                    listitem=list_item, isFolder=True)

    # Add sort methods for the virtual folder items
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)


def list_libraries():
    list_item = xbmcgui.ListItem()

    # Set images for the list item.
    # Set additional info for the list item using its InfoTag.
    # InfoTag allows to set various information for an item.
    # For available properties and methods see the following link:
    # https://codedocs.xyz/xbmc/xbmc/classXBMCAddon_1_1xbmc_1_1InfoTagVideo.html
    # 'mediatype' is needed for a skin to display info for this ListItem correctly.
    info_tag = list_item.getVideoInfoTag()
    info_tag.setMediaType('video')
    info_tag.setTitle('Movies')
    info_tag.setGenres(['Movies'])

    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=listing
    url = get_url(action='movies')
    # is_folder = True means that this item opens a sub-list of lower level items.
    is_folder = True
    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)
    # Add sort methods for the virtual folder items
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=get_url(action='search'), listitem=xbmcgui.ListItem(label="Search"),
                                isFolder=True)

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=get_url(action='series'),
                                listitem=xbmcgui.ListItem(label="TV Series"),
                                isFolder=True)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)


def list_series(page):
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(HANDLE, 'tvshows')
    # Get the list of videos in the category.
    videos = get_videos('series', page)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label
        list_item = xbmcgui.ListItem(label=video['title'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use only poster for simplicity's sake.
        # In a real-life plugin you may need to set multiple image types.
        list_item.setArt({
            'poster': f"{SETTINGS.getString('baseurl')}{video['poster']}&token={SETTINGS.getString('apitoken')}",
            'fanart': f"{SETTINGS.getString('baseurl')}{video['background']}&token={SETTINGS.getString('apitoken')}",
        })
        # Set additional info for the list item via InfoTag.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        info_tag = list_item.getVideoInfoTag()
        info_tag.setMediaType('series')
        info_tag.setTitle(video['title'])
        info_tag.setPlot(video['overview'])
        info_tag.setYear(video['year'])

        xbmcplugin.addDirectoryItem(handle=HANDLE, url=get_url(action='series-item', itemid=video['id']),
                                    listitem=list_item, isFolder=True)

    if videos:
        url = get_url(action=f"page-series", page=page + 1)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=xbmcgui.ListItem(label="Next Page..."),
                                    isFolder=True)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)


def list_episodes(itemid, season):
    xbmcplugin.setContent(HANDLE, 'episodes')
    # Get the list of videos in the category.
    videos = get_episodes(itemid, season)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label
        list_item = xbmcgui.ListItem(label=video['title'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use only poster for simplicity's sake.
        # In a real-life plugin you may need to set multiple image types.
        list_item.setArt({
            'thumb': f"{SETTINGS.getString('baseurl')}{video['screenshot']}&token={SETTINGS.getString('apitoken')}",
        })
        # Set additional info for the list item via InfoTag.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        info_tag = list_item.getVideoInfoTag()
        info_tag.setMediaType('series')
        info_tag.setTitle(video['title'])
        info_tag.setPlot(video['overview'])

        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        url = get_url(action='play',
                      video=f"{SETTINGS.getString('baseurl')}{video['stream']}&token={SETTINGS.getString('apitoken')}")
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)
    # Add sort methods for the virtual folder items
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_NONE)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)


def list_videos(mediatype, page):
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(HANDLE, mediatype)
    # Get the list of videos in the category.
    videos = get_videos(mediatype, page)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label
        list_item = xbmcgui.ListItem(label=video['title'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use only poster for simplicity's sake.
        # In a real-life plugin you may need to set multiple image types.
        list_item.setArt({
            'poster': f"{SETTINGS.getString('baseurl')}{video['poster']}&token={SETTINGS.getString('apitoken')}",
            'fanart': f"{SETTINGS.getString('baseurl')}{video['background']}&token={SETTINGS.getString('apitoken')}",
        })
        # Set additional info for the list item via InfoTag.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        info_tag = list_item.getVideoInfoTag()
        info_tag.setMediaType(mediatype)
        info_tag.setTitle(video['title'])
        info_tag.setPlot(video['overview'])
        info_tag.setYear(video['year'])

        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        url = get_url(action='play',
                      video=f"{SETTINGS.getString('baseurl')}{video['stream']}&token={SETTINGS.getString('apitoken')}")
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)
    # Add sort methods for the virtual folder items
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)

    if videos:
        url = get_url(action=f"page-{mediatype}", page=page + 1)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=xbmcgui.ListItem(label="Next Page..."),
                                    isFolder=True)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(HANDLE)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    # offscreen=True means that the list item is not meant for displaying,
    # only to pass info to the Kodi player
    play_item = xbmcgui.ListItem(offscreen=True)
    play_item.setPath(path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(HANDLE, True, listitem=play_item)


def search():
    dialog = xbmcgui.Dialog()
    user_input = dialog.input("Search", type=xbmcgui.INPUT_ALPHANUM)

    if user_input:
        request = urllib.request.Request(
            f"{SETTINGS.getString('baseurl')}/api/search?query={user_input}&token={SETTINGS.getString('apitoken')}",
            headers={
                "Content-Type": "application/json"
            })

        with urllib.request.urlopen(request) as response:
            data = response.read()
            response_data = json.loads(data.decode("utf-8"))
            videos = response_data.get("items", [])

            xbmcplugin.setContent(HANDLE, 'movies')

            # Iterate through videos.
            for video in videos:
                # Create a list item with a text label
                list_item = xbmcgui.ListItem(label=video['title'])
                # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
                # Here we use only poster for simplicity's sake.
                # In a real-life plugin you may need to set multiple image types.
                list_item.setArt({
                    'poster': f"{SETTINGS.getString('baseurl')}{video['poster']}&token={SETTINGS.getString('apitoken')}",
                    'fanart': f"{SETTINGS.getString('baseurl')}{video['background']}&token={SETTINGS.getString('apitoken')}",
                })
                # Set additional info for the list item via InfoTag.
                # 'mediatype' is needed for skin to display info for this ListItem correctly.
                info_tag = list_item.getVideoInfoTag()
                info_tag.setMediaType('movie')
                info_tag.setTitle(video['title'])
                info_tag.setPlot(video['overview'])
                info_tag.setYear(video['year'])
                info_tag.setGenres(['Movies'])
                # Set 'IsPlayable' property to 'true'.
                # This is mandatory for playable items!
                list_item.setProperty('IsPlayable', 'true')
                # Create a URL for a plugin recursive call.
                url = get_url(action='play',
                              video=f"{SETTINGS.getString('baseurl')}{video['stream']}&token={SETTINGS.getString('apitoken')}")
                # Add the list item to a virtual Kodi folder.
                # is_folder = False means that this item won't open any sub-list.
                is_folder = False
                # Add our item to the Kodi virtual folder listing.
                xbmcplugin.addDirectoryItem(HANDLE, url, list_item, is_folder)
            # Add sort methods for the virtual folder items
            xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
            xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_VIDEO_YEAR)

            # Finish creating a virtual folder.
            xbmcplugin.endOfDirectory(HANDLE)


def router(param_string):
    # Parse a URL-encoded param_string to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(param_string))
    # Check the parameters passed to the plugin
    if not params:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_libraries()

    elif params['action'] == 'movies':
        # Display the list of videos in a provided category.
        list_videos('movies', page=1)

    elif params['action'] == 'page-movies':
        # Display the list of videos in a provided category.
        list_videos('movies', page=int(params['page']))

    elif params['action'] == 'series':
        # Display the list of videos in a provided category.
        list_series(page=1)

    elif params['action'] == 'page-series':
        # Display the list of videos in a provided category.
        list_series(page=int(params['page']))

    elif params['action'] == 'series-item':
        # Display the list of videos in a provided category.
        list_seasons(itemid=int(params['itemid']))

    elif params['action'] == 'list-episodes':
        # Display the list of videos in a provided category.
        list_episodes(itemid=int(params['itemid']), season=int(params['season']))

    elif params['action'] == 'play':
        # Play a video from a provided URL.
        play_video(params['video'])

    elif params['action'] == 'search':
        search()

    else:
        # If the provided param_string does not contain a supported action
        # we raise an exception. This helps to catch coding errors,
        # e.g. typos in action names.
        raise ValueError(f'Invalid param_string: {param_string}!')


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call param_string
    router(sys.argv[2][1:])
