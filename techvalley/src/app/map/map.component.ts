import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpHeaders, HttpClientModule } from '@angular/common/http';
import { Marker } from './marker';

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.scss']
})
export class MapComponent implements OnInit {

  private lat:number = 42.81294;
  private lng:number = -73.94232;
  public datapoints_url = "http://127.0.0.1:5000/";
  public marker:Marker = null;
  public markers:Array<Marker> = [];

  constructor(private router: Router, private http: HttpClient) {
    this.markers = [];
  }

  ngOnInit() {
    this.http.get<Array<Marker> >(this.datapoints_url).subscribe(data => this.markers = data);
  }

  markerClicked(event:Event, detail_id:Number) {
    this.router.navigate([`/detail/${detail_id}`]);
  }

}
