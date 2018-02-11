import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.scss']
})
export class MapComponent implements OnInit {

  lat:number = 42.81464;
  lng:number = -73.947832;
  detail_id:number = 1;

  constructor(private router: Router) { }

  ngOnInit() { }

  mapClicked(event:Event) {
    console.log('hi');
  }

  markerClicked(event:Event) {
    this.router.navigate([`/detail/${this.detail_id}`]);
  }

  setHeight() {
    console.log(window.screen.height - 200 + 'px');
    return window.screen.height - 200 + 'px';
  }

}
