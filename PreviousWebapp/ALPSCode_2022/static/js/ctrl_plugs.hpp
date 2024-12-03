//
// Created by igkanter on 4/17/18.
//



#ifndef SEMS_CTRL_PLUGS_H
#define SEMS_CTRL_PLUGS_H

#include <iostream>
#include <vector>
using namespace std;

// Headers
vector<string> getList();

string getStatus1( string deviceName );

vector<string> getStatusAll( vector<string> devicesV );

bool off1( string deviceName );

bool offAll( vector<string> devicesV );

bool on1( string deviceName );

bool onAll( vector<string> devicesV );

int ctrl_plugs( string, char);

#endif //SEMS_CTRL_PLUGS_H
