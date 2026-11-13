from pathlib import Path
files=['FingerworkerApp.swift','DeviceStore.swift','Measurement.swift',
       'Training.swift','TrainingStore.swift','TrainingViews.swift','TrainingLog.swift',
       'EndstopFeedback.swift']
refs='\n'.join(f'{i+10:024X} = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {f}; sourceTree = "<group>";}};' for i,f in enumerate(files))
builds='\n'.join(f'{i+20:024X} = {{isa = PBXBuildFile; fileRef = {i+10:024X};}};' for i in range(len(files)))
children=', '.join(f'{i+10:024X}' for i in range(len(files)))
sources=', '.join(f'{i+20:024X}' for i in range(len(files)))
p=f'''// !$*UTF8*$!
{{ archiveVersion = 1; classes = {{}}; objectVersion = 56; objects = {{
{refs}
{builds}
000000000000000000000040 = {{isa = PBXFileReference; lastKnownFileType = audio.wav; path = Resources/endstop-click.wav; sourceTree = "<group>";}};
000000000000000000000041 = {{isa = PBXBuildFile; fileRef = 000000000000000000000040;}};
000000000000000000000042 = {{isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = (000000000000000000000041); runOnlyForDeploymentPostprocessing = 0;}};
000000000000000000000001 = {{isa = PBXProject; attributes = {{LastUpgradeCheck = 1600;}}; buildConfigurationList = 000000000000000000000007; compatibilityVersion = "Xcode 14.0"; developmentRegion = en; knownRegions = (en, Base); mainGroup = 000000000000000000000002; productRefGroup = 000000000000000000000004; projectDirPath = ""; targets = (000000000000000000000005);}};
000000000000000000000002 = {{isa = PBXGroup; children = (000000000000000000000003, 000000000000000000000004); sourceTree = "<group>";}};
000000000000000000000003 = {{isa = PBXGroup; children = ({children}, 000000000000000000000040); path = Fingerworker; sourceTree = "<group>";}};
000000000000000000000004 = {{isa = PBXGroup; children = (000000000000000000000006); name = Products; sourceTree = "<group>";}};
000000000000000000000005 = {{isa = PBXNativeTarget; buildConfigurationList = 000000000000000000000008; buildPhases = (000000000000000000000009, 000000000000000000000042); buildRules = (); dependencies = (); name = Fingerworker; productName = Fingerworker; productReference = 000000000000000000000006; productType = "com.apple.product-type.application";}};
000000000000000000000006 = {{isa = PBXFileReference; explicitFileType = wrapper.application; path = Fingerworker.app; sourceTree = BUILT_PRODUCTS_DIR;}};
000000000000000000000007 = {{isa = XCConfigurationList; buildConfigurations = (000000000000000000000030,000000000000000000000031); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;}};
000000000000000000000008 = {{isa = XCConfigurationList; buildConfigurations = (000000000000000000000032,000000000000000000000033); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release;}};
000000000000000000000009 = {{isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = ({sources}); runOnlyForDeploymentPostprocessing = 0;}};
'''
for ident,name in [(0x30,'Debug'),(0x31,'Release'),(0x32,'Debug'),(0x33,'Release')]:
    settings='CLANG_ENABLE_MODULES = YES; SDKROOT = iphoneos; IPHONEOS_DEPLOYMENT_TARGET = 17.0;'
    if ident>=0x32:
        settings+=' SWIFT_VERSION = 5.0; PRODUCT_BUNDLE_IDENTIFIER = com.fingerworker.app; PRODUCT_NAME = "$(TARGET_NAME)"; GENERATE_INFOPLIST_FILE = YES; INFOPLIST_FILE = Fingerworker/Info.plist; INFOPLIST_KEY_NSBluetoothAlwaysUsageDescription = "Fingerworker uses Bluetooth to receive force measurements from your device."; INFOPLIST_KEY_UILaunchScreen_Generation = YES; INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES; TARGETED_DEVICE_FAMILY = 1; CODE_SIGN_STYLE = Automatic;'
    p+=f'{ident:024X} = {{isa = XCBuildConfiguration; buildSettings = {{{settings}}}; name = {name};}};\n'
p+='}; rootObject = 000000000000000000000001; }\n'
Path('ios/Fingerworker.xcodeproj/project.pbxproj').write_text(p)
