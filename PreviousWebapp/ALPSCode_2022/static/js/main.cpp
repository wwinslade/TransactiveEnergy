#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <iostream>
//#include <jansson.h>
#include <mysql/mysql.h>
#include "ctrl_plugs.hpp"
//#include <wiringPi.h>
using namespace std;

void turn_socket_on( string, char );    //initialize turn-on function
void turn_socket_off( string, char );    //initialize turn-off function

int main() {


    MYSQL *conn = mysql_init( NULL );    //establish connection with SQL database
    if ( mysql_real_connect( conn, "localhost", "root", "mk530", "test", 0, NULL, 0 ) == NULL ) {
        printf( "MYSQL: Connection failed\n" );
        return 1;
    }

    printf( "MYSQL: Connection successful\n" );

    int numAppliances = -1;                                    //If numAppliances is equal -1, it's not been updated yet
    int *onOffStates = NULL;

    while ( 1 ) {


        


        //extract appliance list from the database
        char query[] = "SELECT applianceID, state, name FROM userSettings ORDER BY applianceID;";
        int mysqlStatus = mysql_query( conn, query );

        if ( mysqlStatus ) {
            printf( "MYSQL: Query Unsuccessful\n" );
            return 1;
        }
        else {
            printf( "MYSQL: Query Successful\n" );
        }

        MYSQL_RES *mysqlResult = mysql_store_result( conn );                        //store the list

        int numRows = mysql_num_rows( mysqlResult );                            //get number of rows on the list
        int numFields = mysql_field_count( conn );                            //get number of columns
        printf( "MYSQL: Queried %i rows with %i fields each\n", numRows, numFields );

        if ( numAppliances == -1 ) {                                    //Check if
            int j;
            onOffStates = (int*)malloc( sizeof( int ) * numRows );    //malloc: allocates a block of "size" bytes of memory
            for ( j = 0; j < numRows; j++ ) {
                onOffStates[j] = -1;
            }
            numAppliances = numRows;
        }

        else if ( numAppliances != numRows ) {
            int j;
            //free();   // what's been free here????????????????????
            onOffStates = (int*)malloc( sizeof( int ) * numRows );
            for ( j = 0; j < numRows; j++ ) {
                onOffStates[j] = -1;
            }
            numAppliances = numRows;
        }

        MYSQL_ROW mysqlRow;
        int i = 0;
        while ( mysqlRow = mysql_fetch_row( mysqlResult ) ) {

            string device =  mysqlRow[2];   //gets device name
            char action = mysqlRow[1][0];   // gets device action
            onOffStates[i] = ctrl_plugs(device, 's'); // gets status

            if ( mysqlRow[1][0] == '1' ) {
                if ( onOffStates[i] != 1 ) {
                    printf( "Turning appliance %d on\n", i );
                    //Call the function to turn on the outlet.
                    // Basically, this is what you want to change to implement the Wifi outlet.
                    //string device =  mysqlRow[2];
                    //char action = mysqlRow[1][0];
                    turn_socket_on( device, action );
                    onOffStates[i] = 1;



                }
                else {
                    printf( "Appliance %d is already on, skipping\n", i );
                }
            }
            else {
                if ( onOffStates[i] != 0 ) {
                    printf( "Turning appliance %d off\n", i );
                    //string device =  mysqlRow[2];
                    //int action = mysqlRow[1][0];
                    turn_socket_off( device, action );
                    onOffStates[i] = 0;  //Call the function to turn off the outlet. You need to change this one too
                }
                else {
                    printf( "Appliance %d is already off, skipping\n", i );        //
                }
            }
            i++;
        }
        mysql_free_result( mysqlResult );                    //delete the list
        //  delay(100);
    }
    mysql_close( conn );                            //remove the connection with SQL
}


void turn_socket_on( string device, char action ) {

    ctrl_plugs(device, action);
}


void turn_socket_off( string device, char action ) {
    ctrl_plugs(device, action);
}