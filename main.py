from kivymd.app import MDApp
import os
from kivy.lang import Builder
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.theming import ThemeManager
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRoundFlatButton
import deso
from deso import Identity
from kivy.properties import StringProperty
import pickle
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarListItem


global loggedIn
global user
global publicKey
loggedIn = False
user = ""
publicKey = ""

# pickles the current settings
def pickle_settings(settings):
    with open('temp/settings.pickle', 'wb') as handle:
        pickle.dump(settings, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("settings pickled")

# unpickles the current settings
def unpickle_settings():
    if os.path.exists('temp/settings.pickle'):
        print("settings not found")
        with open('temp/settings.pickle', 'rb') as handle:
	        settings = pickle.load(handle)
    else:
        settings = {}        
    
    return settings

# unpickles the user's profile
def unpickle_profile():
    with open('temp/profile.pickle', 'rb') as handle:
        profile = pickle.load(handle)
        #print("profile unpickled")
    return profile

# pickles the user's profile
def pickle_profile(profile):
    #encrypt profile with secret key

    if not os.path.exists('temp/settings.pickle'):
        os.makedirs('temp')

    with open('temp/profile.pickle', 'wb') as handle:
        pickle.dump(profile, handle, protocol=pickle.HIGHEST_PROTOCOL)
        #print("profile pickled")


# class for the avatar circle
class CircularAvatarImage(MDCard):
    avatar = StringProperty()
    name = StringProperty()

# class for the story creator


class StoryCreator(MDCard):
    avatar = StringProperty()

class SeedVerifyScreen(MDScreen):
    pass
    
# Create the signup screen
class SignupScreen(MDScreen):
    pass

# Create the login screen
class LoginScreen(MDScreen):
    pass

#create the login with seed phrase screen
class SeedLoginScreen(MDScreen):
    seedPhrase = StringProperty("")
    userName = StringProperty("")

    def textInput(self, widget):
        self.seedPhrase = widget.text
        
    def nameInput(self, widget):
        self.userName = widget.text

    def onClick(self):
        self.textInput(self.ids.seedphrase)
        self.nameInput(self.ids.userName)
        seedphrase = self.seedPhrase
        #print(self.seedPhrase, 'seed phrase')
        #validate seedphrase has 12 words
        if len(seedphrase.split()) != 12:
            toast("Seed phrase must have 12 words")
            return
        #try to get seed hex from seed phrase catch error if seed phrase is invalid
        try:        
            SEED_HEX = Identity.getSeedHexFromSeedPhrase(seedphrase)
        except:
            toast("Invalid seed phrase")
            return
        #print(SEED_HEX, 'seed hex')
        #print(self.userName, 'username')
        #get user profile and pickle it
        desoUser = deso.User()
        profile = desoUser.getSingleProfile(username=self.userName).json()
        #print(profile)
        if 'error' in profile:
            toast(profile['error'])
        else:
            pickle_profile(profile)
            global user
            global loggedIn
            global publicKey
            loggedIn = True
            user=self.userName
            publicKey=profile['Profile']['PublicKeyBase58Check']
            settings = {}
            settings['user'] = self.userName
            settings['loggedIn'] = True
            settings['seedHex'] = SEED_HEX
            settings['publicKey'] = publicKey
            pickle_settings(settings)

            self.manager.current = 'homepage_read_only'

class UserNameLoginScreen(MDScreen):
    userName = StringProperty("")

    def textInput(self, widget):
        self.userName = widget.text

    def onClick(self):
        self.textInput(self.ids.username)
        desoUser = deso.User()
        profile = desoUser.getSingleProfile(username=self.userName).json()
        if 'error' in profile:
            toast(profile['error'])
        else:
            pickle_profile(profile)
            global user
            global loggedIn
            loggedIn = False
            user=self.userName
            settings = {}
            settings['user'] = self.userName
            settings['loggedIn'] = False
            pickle_settings(settings)
            self.manager.current = 'homepage_read_only'
            
        self.current = 'homepage_read_only'



# Create the homepage read only screen
class HomePageReadOnlyScreen(MDScreen):
    profile_picture = StringProperty("") #'https://avatars.githubusercontent.com/u/89080192?v=4'
    username = StringProperty("")
    desoprice = StringProperty("")
    avatar = StringProperty("")
    dialog = None
    
    def on_enter(self):
        profile = unpickle_profile()
        print(profile)
        print(profile['Profile']['Username'])
        username=profile['Profile']['Username']
        self.username = profile['Profile']['Username']
        self.profile_picture = deso.User().getProfilePicURL(
                    profile['Profile']['PublicKeyBase58Check'])
        
        print(user, 'printed user here')

    def logout(self):
        settings = {}
        
        pickle_settings(settings)
        global loggedIn
        loggedIn = False
        self.manager.current = 'login'


   
   

# Create the main app
class MainApp(MDApp):

    def build(self):
        # Set the theme
        self.theme_cls.theme_style = "Light"
        # Create the screen manager
        sm = ScreenManager()
        Builder.load_file('signup.kv')# Add the screens to the screen manager
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(UserNameLoginScreen(name='username_login'))
        sm.add_widget(HomePageReadOnlyScreen(name='homepage_read_only'))
        sm.add_widget(SeedVerifyScreen(name='seed_verify'))
        sm.add_widget(SeedLoginScreen(name='seed_login'))
        
        
        #check to see if logged in and go to homepage
        settings=unpickle_settings()
        print('settings are here', settings)
        if settings:
            global loggedIn
            loggedIn = True
            sm.current = 'homepage_read_only'

        return sm

    



# Run the app
if __name__ == '__main__':
    MainApp().run()
