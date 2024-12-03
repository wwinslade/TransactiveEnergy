#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <jansson.h>
#include <mysql.h>
#include <wiringPi.h>


void turn_socket_on( int pin );    //initialize turn-on function
void turn_socket_off( int pin );    //initialize turn-off function

int main() {


    MYSQL *conn = mysql_init( NULL );    //establish connection with SQL database
    if ( mysql_real_connect( conn, "localhost", "root", "root", "test", 0, NULL, 0 ) == NULL ) {
        printf( "MYSQL: Connection failed\n" );
        return 1;
    }

    printf( "MYSQL: Connection successful\n" );

    int numAppliances = -1;                                    //If numAppliances is equal -1, it's not been updated yet
    int *onOffStates = NULL;

    while ( 1 ) {
        //extract appliance list from the database
        char *query = "SELECT applianceID, state FROM userSettings ORDER BY applianceID;";
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
            onOffStates = malloc( sizeof( int ) * numRows );    //malloc: allocates a block of "size" bytes of memory
            for ( j = 0; j < numRows; j++ ) {
                onOffStates[j] = -1;
            }
            numAppliances = numRows;
        }

        else if ( numAppliances != numRows ) {
            int j;
            free();
            onOffStates = malloc( sizeof( int ) * numRows );
            for ( j = 0; j < numRows; j++ ) {
                onOffStates[j] = -1;
            }
            numAppliances = numRows;
        }

        MYSQL_ROW mysqlRow;
        int i = 0;
        while ( mysqlRow = mysql_fetch_row( mysqlResult ) ) {
            if ( mysqlRow[1][0] == '1' ) {
                if ( onOffStates[i] != 1 ) {
                    printf( "Turning appliance %d on\n", i );
                    //Call the function to turn on the outlet.
                    // Basically, this is what you want to change to implement the Wifi outlet.
                    turn_socket_on( i );


                    [i] = 1;
                }
                else {
                    printf( "Appliance %d is already on, skipping\n", i );
                }
            }
            else {
                if ( onOffStates[i] != 0 ) {
                    printf( "Turning appliance %d off\n", i );
                    turn_socket_off( i );
                    onOffStates[i] = 0;                        //Call the function to turn off the outlet. You need to change this one too
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


void turn_socket_on( int pin ) {
    pinMode( transmitPin, OUTPUT );
    int j;
    for ( j = 0; j < numberAttempt; ++j ) {

        int i;
        for ( i = 0; i < 25; ++i ) {
            if ( socket_on[pin][i] == '1' ) {
                digitalWrite( transmitPin, HIGH );
                delayMicroseconds( short_delay );
                digitalWrite( transmitPin, LOW );
                delayMicroseconds( long_delay );
            }
            else if ( socket_on[pin][i] == '0' ) {
                digitalWrite( transmitPin, HIGH );
                delayMicroseconds( long_delay );
                digitalWrite( transmitPin, LOW );
                delayMicroseconds( short_delay );
            }
        }
        digitalWrite( transmitPin, LOW );
        delayMicroseconds( extended_delay );
    }
}


void turn_socket_off( int pin ) {
    pinMode( transmitPin, OUTPUT );
    int j;
    for ( j = 0; j < numberAttempt; ++j ) {

        int i;
        for ( i = 0; i < 25; ++i ) {
            if ( socket_off[pin][i] == '1' ) {
                digitalWrite( transmitPin, HIGH );
                delayMicroseconds( short_delay );
                digitalWrite( transmitPin, LOW );
                delayMicroseconds( long_delay );
            }
            else if ( socket_off[pin][i] == '0' ) {
                digitalWrite( transmitPin, HIGH );
                delayMicroseconds( long_delay );
                digitalWrite( transmitPin, LOW );
                delayMicroseconds( short_delay );
            }
        }
        digitalWrite( transmitPin, LOW );
        delayMicroseconds( extended_delay );
    }
} 
