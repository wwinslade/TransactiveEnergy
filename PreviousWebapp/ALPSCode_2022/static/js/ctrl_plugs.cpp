#include <stdio.h>
#include <stdlib.h>
#include <cstdlib>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <string.h>
#include <algorithm>
#include "ctrl_plugs.hpp"

using namespace std;



int ctrl_plugs( string deviceName, char actionC ) {
    vector<string> devicesVInMain;
    string action = "\0";
    bool nameOnList = false;
    bool needSpace = false;
    string status;
    bool success;

    if (actionC == '0') action = "off";
    else if (actionC == '1') action = "on";
    else action = "status";

    /* Verify the program was run correctly with: name of program, device name (or all), and action.
       if not, shutdown with error */
//    if ( argc < 3 ) {
//        cout << "ctrl_plugs: error: too few arguments" << endl
//             << "positional arguments:" << endl
//             << " device      Name or alias of the device" << endl
//             << " state       'on' or 'off' or 'status' " << endl;
//        return 0;
//    }

    //action = argv[argc - 1];
    /* Lower case all the letter of the action */
    //transform( action.begin(), action.end(), action.begin(), ::tolower );

    /* Checks if action is valid*/
//    if ( action != "on" && action != "off" && action != "status" ) {
//        cout << "Action or state is not valid" << endl
//             << "arguments:" << endl
//             << " state       'on' or 'off' or 'status' " << endl;
//        return 0;
//    }

    system( "/bin/bash -c /home/SEMS/activate.sh" ); // turn on the shell
    devicesVInMain = getList();                    // gets device list

    /* Extract the device name
//        Takes care if device name is more than 1 word */
//    for ( int i = 1; i < argc - 1; i++ ) {
//        if ( needSpace == true )
//            deviceName += " ";
//        deviceName += argv[i];
//        needSpace = true;
//    }

    /* If referring to a specific device */
    if ( deviceName != "ALL" && deviceName != "all" && deviceName != "All" ) {

        /* Checks if device is on the list */
        for ( int i = 0; i < devicesVInMain.size(); i++ ) {
            if ( deviceName == devicesVInMain[i] )
                nameOnList = true; // device is on the list
        }
        if ( !(nameOnList) ) {
            // gets the list of devices and save it to a text file
            cout << "looking for devices\n\n";
            system( "/bin/bash -c /home/SEMS/list.sh" );
            devicesVInMain = getList(); // gets device list
            /* Checks if device is on the list */
            for ( int i = 0; i < devicesVInMain.size(); i++ ) {
                if ( deviceName == devicesVInMain[i] )
                    nameOnList = true; // device is on the list
            }
            if ( !(nameOnList) ) {

                cout << "Error: Device name is not on the network or device name is wrong." << endl
                     << "    check the device connection or device name and try again...\n\n"
                     << "arguments:" << endl
                     << " device      Name or alias of the device" << endl;
                return 0;
            }
        }
    }
    else {
        if ( devicesVInMain.size() < 8 ) {
            cout << "looking for devices\n\n";
            system( "/bin/bash -c /home/SEMS/list.sh" );
            devicesVInMain = getList(); // gets device list
        }
    }

    /* Choose action */
    if ( action == "on" ) {

        if ( deviceName == "ALL" || deviceName == "all" ) {
            onAll( devicesVInMain );
        }
        else {

            success = on1( deviceName );
        }
    }
    else if ( action == "off" ) {
        if ( deviceName == "ALL" || deviceName == "all" ) {
            offAll( devicesVInMain );
        }
        else {

            success = off1( deviceName );
        }
    }
    else // Default: status of device
    {
        if ( deviceName == "ALL" || deviceName == "all" ) {
            getStatusAll( devicesVInMain );
        }
        else {
            status = getStatus1( deviceName );
            if (status == "on") return 1;
            if (status == "off") return 0;
        }
    }
}

/*
* Gets the lists of plugs connected to the network
* ./wemo list
*/
vector<string> getList() {

    vector<string> devicesV; // vector to holds devices name

    // gets the list of devices and save it to a text file
    //system("/bin/bash -c /home/SEMS/list.sh");

    ifstream devicesFile;            //open an input channel
    devicesFile.open( "devices.txt" ); // open the devices list file
    if ( devicesFile.is_open() ) { // verify file is open

        // Read all devices until end of file
        string tempS; // holds a temp string (device name)
        while ( getline( devicesFile, tempS ) ) {
            tempS = tempS.substr( 13, tempS.length() - 15 ); // extracts device name
            devicesV.push_back( tempS );                     // push to a vector

        }
        devicesFile.close();
    }
    else {
        cout << "The file did not open successfully! Existing...\n";
        exit; // devices.txt is not open... exit
    }

    return ( devicesV );
}

/*
* Gets the status of one device
*/
string getStatus1( string deviceName ) {
    string returnVal;

    string temp = "wemo -v switch \"" + deviceName + "\" " + "status > status.txt";
    system( temp.c_str() ); // gets the status of the device

    ifstream statusFile; //open an input channel
    /* open the file containing the status of the device */
    statusFile.open( "status.txt" );
    if ( statusFile.is_open() ) {                                   // verify file is open
        getline( statusFile, returnVal ); //read the status of the device
        statusFile.close();
    }
    else
        exit; // device is not open... exit

    return ( returnVal );
}

/*
* Gets the status of all devices connected to the network
*/
vector<string> getStatusAll( vector<string> devicesV ) {
    string temp;
    vector<string> statuses;

    temp = "wemo -v switch \"" + devicesV[0] + "\" " + "status > status.txt";
    system( temp.c_str() ); // gets the status of the device
    for ( int i = 1; i < devicesV.size(); i++ ) {
        temp = "\0";
        temp = "wemo -v switch \"" + devicesV[i] + "\" " + "status >> status.txt";
        system( temp.c_str() ); // gets the status of the device
    }

    ifstream statusFile; //open an input channel
    /* open the file containing the status of the device */
    statusFile.open( "status.txt" );
    if ( statusFile.is_open() ) { // verify file is open

        // Read all devices until end of file
        string tempS; // holds a temp string (device name)
        while ( getline( statusFile, tempS ) ) {
            statuses.push_back( tempS ); // push to a vector
        }
        statusFile.close();
    }
    else
        exit; // status file is not open... exit
    return ( statuses );
}

/*
* Turns 1 device off
*/
bool off1( string deviceName ) {
    string status;

    string temp = "wemo switch \"" + deviceName + "\" " + "off";
    system( temp.c_str() ); // turn device off;

    status = getStatus1( deviceName ); //call the get status function
    if ( status == "off" )
        return true;
    else
        return false;
}

/*
* Turns all devices off
*/
bool offAll( vector<string> devicesV ) {
    vector<string> statuses;
    statuses.resize( devicesV.size() );
    bool wrongStatus = false;

    for ( int i = 0; i < devicesV.size(); i++ ) {
        string temp = "wemo switch \"" + devicesV[i] + "\" " + "off";
        system( temp.c_str() ); // turn device on;
        /* call the get status function and saves return value to vector */
        statuses[i] = ( getStatus1( devicesV[i] ) );
        if ( statuses[i] != "iff" )
            wrongStatus = true;
    }

    if ( wrongStatus == true )
        return false;

    return true;
}

/*
* Turns 1 device on
*/
bool on1( string deviceName ) {

    string status;

    string temp = "wemo switch \"" + deviceName + "\" " + "on";
    system( temp.c_str() ); // turn device on;

    status = getStatus1( deviceName ); //call the get status function
    if ( status == "on" )
        return true;
    else
        return false;
}

/*
* Turns all devices on
*/
bool onAll( vector<string> devicesV ) {
    vector<string> statuses;
    statuses.resize( devicesV.size() );
    bool wrongStatus = false;

    for ( int i = 0; i < devicesV.size(); i++ ) {
        string temp = "wemo switch \"" + devicesV[i] + "\" " + "on";
        system( temp.c_str() ); // turn device on;
        /* call the get status function and saves return value to vector */
        statuses[i] = ( getStatus1( devicesV[i] ) );
        if ( statuses[i] != "on" )
            wrongStatus = true;
    }

    if ( wrongStatus == true )
        return false;

    return true;
}
